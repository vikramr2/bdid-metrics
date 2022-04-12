import requests
import pandas as pd


API_KEY = 'PASTE API KEY HERE'
API_VERSION = 523


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
    for i in range(num_api_calls_required):
        call_offset = api_call_batch_size * i  # increase offset by batch size after each call
        url_params['offset'] = call_offset
        call_r = requests.get(url=request_url, params=url_params, headers=headers)
        if call_r.status_code != 200:
            print(f'WARNING: API returned non-200 ({r.status_code}) status code on call {i}')
            continue
        call_pubs = call_r.json().get('items', [])  # gets us list of pubs retrieved in this api call
        all_pubs.extend(call_pubs)

    pubs_df = pd.DataFrame(all_pubs)
    return pubs_df


if __name__ == '__main__':
    harley_email_id = 'htj@illinois.edu'
    # harley_pure_id = 3023571
    harley_pubs_df = get_research_projects_by_id(person_id=harley_email_id)
    harley_pubs_df.to_csv(f'harley_publications.csv', index=False)
    # df = pd.read_csv('harley_publications.csv')  # to read file
