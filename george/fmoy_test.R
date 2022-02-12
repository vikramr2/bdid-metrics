# test script to see R and data.table can calculate Bu's measurements
# The proportional calculations can be performed later
# George Chacko 2/12/2022

rm(list = ls())
library(data.table)
# ptm <- proc.time()
i=1
x <- fread("citing_cited_network.integer.tsv")
setkey(x, V2)

# vector of all nodes with at least one edge (either citing or cited)
bigvec <- x[, unique(V2)]

# chunking first element of bigvec => tenec focal publications
littlevec <- bigvec[1:1000000]

# get citing articles for littlevec
c <- x[V2 %in% littlevec] 

# get references of littlevec
r <- x[V1 %in% littlevec]

# from parent dataset (x) get all edges involving neighbors of nodes in c
cc <- x[V1 %in% c$V1 | V2 %in% c$V2]

# from parent dataset (x) get all edges involving neighbors of nodes in r
rr <- x[V1 %in% r$V1 | V2 %in% r$V2]

# small for loop
df <- data.frame()

for (i in 1:length(littlevec)) {

# pubs citing littlevec[i]
citers <- cc[V2 == littlevec[i]]
# pubs cited by littlevec[i]
citeds <- rr[V1 == littlevec[i] ]

# count of links from citers of a focal pub to its references 
citer_cited <- cc[V2 %in% citeds$V2 & V1 %in% citers$V1]
tr_cited_pub <- dim(citer_cited)[1]

# count of pubs citing focal pub that also cite a reference of a focal pub
cp_r_cited_pub_nonzero <- length(unique(citer_cited$V1))

# count of pubs citing focal pub that do not cite a reference of a focal pub
cp_r_cited_pub_zero <- tr_cited_pub - cp_r_cited_pub_nonzero


# For citers of a focal pub that cite each other
citers_citers <- cc[V1 %in% citers$V1 & V2 %in% citers$V1]
# count of links from citers of a focal pub to its other citers
tr_citing_pub <- dim(citers_citers)[1]
# count of pubs citing focal pub that also cite a citer of a focal pub
cp_r_citing_pub_nonzero <- dim(citers_citers[, .N, by = "V2"])[1]
# count of pubs citing focal pub that do not cite a citer of a focal pub
cp_r_citing_pub_zero <- tr_citing_pub - cp_r_citing_pub_nonzero

tmp <- c(littlevec[i],tr_citing_pub, cp_r_citing_pub_nonzero, cp_r_citing_pub_zero,
			tr_cited_pub, cp_r_cited_pub_nonzero, cp_r_cited_pub_zero)
df <- rbind(df,tmp)
colnames(df) <- c('fp','tr_citing_pub', 'cp_r_citing_pub_nonzero', 'cp_r_citing_pub_zero',
			'tr_cited_pub', 'cp_r_cited_pub_nonzero', 'cp_r_cited_pub_zero')
}
fwrite(df,file=paste0('bu-6param_',i,'csv'))



