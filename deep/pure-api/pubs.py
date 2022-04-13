import requests
import pandas as pd


API_KEY = 'PASTE API KEY HERE'
API_VERSION = 523


def capture_relevant_fields(pubs_all_fields: list):
    """
    Sort through raw JSON from pubs API and filter down to relevant fields
    :param pubs_all_fields: list of dictionaries from raw JSON for multiple pubs from pubs API
    :return: list of filtered dictionaries with relevant fields only
    """
    pubs_relevant_fields = list()

    for pub in pubs_all_fields:
        pub_relevant_fields = dict()
        pub_relevant_fields['external_id'] = pub.get('externalId', None)
        pub_relevant_fields['title'] = pub.get('title', {}).get('value', '')
        pub_relevant_fields['pages'] = pub.get('pages', '')
        pub_relevant_fields['volume'] = pub.get('volume', '')
        pub_relevant_fields['journal_title'] = pub.get('journalAssociation', {}).get('title', {}).get('value', '')
        pub_relevant_fields['journal_issn'] = pub.get('journalAssociation', {}).get('issn', {}).get('value', '')
        pub_relevant_fields['total_number_of_authors'] = pub.get('totalNumberOfAuthors', None)

        # get all author firstnames and lastnames, comma-separated in one field
        person_associations = pub.get('personAssociations', [])
        author_names = ''
        for i, author in enumerate(person_associations):
            name = author.get('name', {})
            author_names += f"{name.get('firstName', '')} {name.get('lastName', '')}".strip()
            if i < len(person_associations)-1:
                author_names += ', '
        pub_relevant_fields['author_names'] = author_names

        electronic_versions = pub.get('electronicVersions', [])
        pub_relevant_fields['doi'] = ''
        if len(electronic_versions) > 0:
            pub_relevant_fields['doi'] = electronic_versions[0].get('doi', '')

        publication_statuses = pub.get('publicationStatuses', [])
        pub_relevant_fields['year'] = None
        if len(publication_statuses) > 0:
            pub_relevant_fields['year'] = publication_statuses[0].get('publicationDate', {}).get('year', None)

        pubs_relevant_fields.append(pub_relevant_fields)

    return pubs_relevant_fields


def get_research_projects_by_id(person_id):
    """
    Given email or Pure Id of researcher, get all publication details of that researcher
    :param person_id: email or Pure Id of researcher
    :return: Pandas Dataframe with publication details if found, None otherwise
    """
    api_url = 'https://experts.illinois.edu/ws/api'
    api_endpoint = f'persons/{person_id}/research-outputs'
    api_call_batch_size = 50  # number of pubs to retrieve per call
    url_params = {'apiKey': API_KEY, 'size': api_call_batch_size}
    headers = {'Accept': 'application/json'}
    request_url = f'{api_url}/{API_VERSION}/{api_endpoint}'

    r = requests.get(url=request_url, params=url_params, headers=headers)
    if r.status_code != 200:
        print(f'ERROR: API returned non-200 ({r.status_code}) status code')
        return None

    pubs_count = r.json().get('count', 0)
    if pubs_count <= 0:
        print(f'Person with id {person_id} does not have any publications')
        return None

    # Determine number of API calls required
    num_remainder_calls = 1 if (pubs_count % api_call_batch_size) > 0 else 0
    num_api_calls_required = (pubs_count // api_call_batch_size) + num_remainder_calls

    # Make API calls and retrieve data
    all_pubs = list()
    all_pubs_relevant_fields = list()
    for i in range(num_api_calls_required):
        call_offset = api_call_batch_size * i  # increase offset by batch size after each call
        url_params['offset'] = call_offset
        call_r = requests.get(url=request_url, params=url_params, headers=headers)
        if call_r.status_code != 200:
            print(f'WARNING: API returned non-200 ({r.status_code}) status code on call {i}')
            continue
        call_pubs = call_r.json().get('items', [])  # gets us list of pubs retrieved in this api call
        all_pubs.extend(call_pubs)

        call_pubs_relevant_fields = capture_relevant_fields(call_pubs)  # select only certain relevant fields
        all_pubs_relevant_fields.extend(call_pubs_relevant_fields)

    pubs_df = pd.DataFrame(all_pubs_relevant_fields)
    return pubs_df


if __name__ == '__main__':
    harley_email_id = 'htj@illinois.edu'
    # harley_pure_id = 3023571
    harley_pubs_df = get_research_projects_by_id(person_id=harley_email_id)
    harley_pubs_df.to_csv(f'harley_publications_relevant_fields.csv', index=False)
    # df = pd.read_csv('harley_publications.csv')  # to read file
