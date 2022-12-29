library(data.table)
setwd('~/Desktop/SNAP')

system('ls *.csv')

# *** wiki-talk ***
wiki_talk <- fread('wiki_talk_cm_df.csv')
# remove cm output before cM-universl treatment
wiki_talk <- wiki_talk[grep("preprocessed", wiki_talk$Rx, invert = TRUE), ]
# wiki_talk <- wiki_talk[grep("nontree_clusters", wiki_talk$Rx, invert = TRUE), ]
t <- sort(wiki_talk$Rx,decreasing=TRUE)
wiki_talk$Rx <- factor(wiki_talk$Rx,levels=t)
wiki_talk[grep("leiden.5",Rx),gp:="leiden.5"]
wiki_talk[grep("leiden.1",Rx),gp:="leiden.1"]
wiki_talk[grep("leiden.01",Rx),gp:="leiden.01"]
wiki_talk[grep("leiden.001",Rx),gp:="leiden.001"]
#
wiki_talk[grep("r2nontree_clusters",Rx),gp2:="r2tree"]
wiki_talk[grep("r2nontree_n10_clusters",Rx),gp2:="r2tree_size"]
wiki_talk[grep("after",Rx),gp2:="cm1"]
#
wiki_talk1 <- wiki_talk[!is.na(gp2),]
wiki_talk2 <- wiki_talk[is.na(gp2),]
wiki_talk2[Rx %like% "leiden.[0-9]+_nontree_clusters.tsv",gp2:='tree']
wiki_talk2[Rx %like% "leiden.[0-9]+_nontree_n10_clusters.tsv",gp2:='tree_size']
wiki_talk2[is.na(gp2),gp2:='leiden']
wiki_talk3 <- rbind(wiki_talk1,wiki_talk2)
wiki_talk3$gp <- factor(wiki_talk3$gp, levels=c('leiden.5','leiden.1','leiden.01','leiden.001'))
wiki_talk3$gp2 <- factor(wiki_talk3$gp2, levels=c('leiden','tree','tree_size','cm1','r2tree','r2tree_size'))
wiki_talk3 <- wiki_talk3[order(gp,gp2)]
#
p_wiki_talk <- ggplot(data=wiki_talk3, aes(x=gp2, y=node_cov)) +  geom_bar(stat="identity", fill="steelblue") + facet_wrap(~ gp) + ylim(0,1)
pdf('wiki_talk.pdf')
print(p_wiki_talk)
dev.off()
p_wiki_talk
wiki_talk
wiki_talk3

# *** cen ***

cen <- fread('cen_cm_df.csv')
# remove cm output before cM-universl treatment
cen <- cen[grep("preprocessed", cen$Rx, invert = TRUE), ]
# cen <- cen[grep("nontree_clusters", cen$Rx, invert = TRUE), ]
t <- sort(cen$Rx,decreasing=TRUE)
cen$Rx <- factor(cen$Rx,levels=t)
cen[grep("leiden.5",Rx),gp:="leiden.5"]
cen[grep("leiden.1",Rx),gp:="leiden.1"]
cen[grep("leiden.01",Rx),gp:="leiden.01"]
cen[grep("leiden.001",Rx),gp:="leiden.001"]
#
cen[grep("r2nontree_clusters",Rx),gp2:="r2tree"]
cen[grep("r2nontree_n10_clusters",Rx),gp2:="r2tree_size"]
cen[grep("after",Rx),gp2:="cm1"]
#
cen1 <- cen[!is.na(gp2),]
cen2 <- cen[is.na(gp2),]
cen2[Rx %like% "leiden.[0-9]+_nontree_clusters.tsv",gp2:='tree']
cen2[Rx %like% "leiden.[0-9]+_nontree_n10_clusters.tsv",gp2:='tree_size']
cen2[is.na(gp2),gp2:='leiden']
cen3 <- rbind(cen1,cen2)
cen3$gp <- factor(cen3$gp, levels=c('leiden.5','leiden.1','leiden.01','leiden.001'))
cen3$gp2 <- factor(cen3$gp2, levels=c('leiden','tree','tree_size','cm1','r2tree','r2tree_size'))
cen3 <- cen3[order(gp,gp2)]
#
p_cen <- ggplot(data=cen3, aes(x=gp2, y=node_cov)) +  geom_bar(stat="identity", fill="steelblue") + facet_wrap(~ gp) + ylim(0,1)
pdf('cen.pdf')
print(p_cen)
dev.off()
p_cen
cen
cen3

# *** cit_patents ***

cit_patents <- fread('cit_patents_cm_df.csv')
# remove cm output before cM-universl treatment
cit_patents <- cit_patents[grep("preprocessed", cit_patents$Rx, invert = TRUE), ]
# cit_patents <- cit_patents[grep("nontree_clusters", cit_patents$Rx, invert = TRUE), ]
t <- sort(cit_patents$Rx,decreasing=TRUE)
cit_patents$Rx <- factor(cit_patents$Rx,levels=t)
cit_patents[grep("leiden.5",Rx),gp:="leiden.5"]
cit_patents[grep("leiden.1",Rx),gp:="leiden.1"]
cit_patents[grep("leiden.01",Rx),gp:="leiden.01"]
cit_patents[grep("leiden.001",Rx),gp:="leiden.001"]
#
cit_patents[grep("r2nontree_clusters",Rx),gp2:="r2tree"]
cit_patents[grep("r2nontree_n10_clusters",Rx),gp2:="r2tree_size"]
cit_patents[grep("after",Rx),gp2:="cm1"]
#
cit_patents1 <- cit_patents[!is.na(gp2),]
cit_patents2 <- cit_patents[is.na(gp2),]
cit_patents2[Rx %like% "leiden.[0-9]+_nontree_clusters.tsv",gp2:='tree']
cit_patents2[Rx %like% "leiden.[0-9]+_nontree_n10_clusters.tsv",gp2:='tree_size']
cit_patents2[is.na(gp2),gp2:='leiden']
cit_patents3 <- rbind(cit_patents1,cit_patents2)
cit_patents3$gp <- factor(cit_patents3$gp, levels=c('leiden.5','leiden.1','leiden.01','leiden.001'))
cit_patents3$gp2 <- factor(cit_patents3$gp2, levels=c('leiden','tree','tree_size','cm1','r2tree','r2tree_size'))
cit_patents3 <- cit_patents3[order(gp,gp2)]
#
p_cit_patents <- ggplot(data=cit_patents3, aes(x=gp2, y=node_cov)) +  geom_bar(stat="identity", fill="steelblue") + facet_wrap(~ gp) + ylim(0,1)
pdf('cit_patents.pdf')
print(p_cit_patents)
dev.off()
p_cit_patents
cit_patents
cit_patents3


# *** cit_hepph ***
cit_hepph <- fread('cit_hepph_cm_df.csv')
# remove cm output before cM-universl treatment
cit_hepph <- cit_hepph[grep("preprocessed", cit_hepph$Rx, invert = TRUE), ]
# cit_hepph <- cit_hepph[grep("nontree_clusters", cit_hepph$Rx, invert = TRUE), ]
t <- sort(cit_hepph$Rx,decreasing=TRUE)
cit_hepph$Rx <- factor(cit_hepph$Rx,levels=t)
cit_hepph[grep("leiden.5",Rx),gp:="leiden.5"]
cit_hepph[grep("leiden.1",Rx),gp:="leiden.1"]
cit_hepph[grep("leiden.01",Rx),gp:="leiden.01"]
cit_hepph[grep("leiden.001",Rx),gp:="leiden.001"]
#
cit_hepph[grep("r2nontree_clusters",Rx),gp2:="r2tree"]
cit_hepph[grep("r2nontree_n10_clusters",Rx),gp2:="r2tree_size"]
cit_hepph[grep("after",Rx),gp2:="cm1"]
#
cit_hepph1 <- cit_hepph[!is.na(gp2),]
cit_hepph2 <- cit_hepph[is.na(gp2),]
cit_hepph2[Rx %like% "leiden.[0-9]+_nontree_clusters.tsv",gp2:='tree']
cit_hepph2[Rx %like% "leiden.[0-9]+_nontree_n10_clusters.tsv",gp2:='tree_size']
cit_hepph2[is.na(gp2),gp2:='leiden']
cit_hepph3 <- rbind(cit_hepph1,cit_hepph2)
cit_hepph3$gp <- factor(cit_hepph3$gp, levels=c('leiden.5','leiden.1','leiden.01','leiden.001'))
cit_hepph3$gp2 <- factor(cit_hepph3$gp2, levels=c('leiden','tree','tree_size','cm1','r2tree','r2tree_size'))
cit_hepph3 <- cit_hepph3[order(gp,gp2)]
#
p_cit_hepph <- ggplot(data=cit_hepph3, aes(x=gp2, y=node_cov)) +  geom_bar(stat="identity", fill="steelblue") + facet_wrap(~ gp) + ylim(0,1)
pdf('cit_hepph.pdf')
print(p_cit_hepph)
dev.off()
p_cit_hepph
cit_hepph
cit_hepph3

# *** orkut ***
orkut <- fread('orkut_cm_df.csv')
# remove cm output before cM-universl treatment
orkut <- orkut[grep("preprocessed", orkut$Rx, invert = TRUE), ]
# orkut <- orkut[grep("nontree_clusters", orkut$Rx, invert = TRUE), ]
t <- sort(orkut$Rx,decreasing=TRUE)
orkut$Rx <- factor(orkut$Rx,levels=t)
orkut[grep("leiden.5",Rx),gp:="leiden.5"]
orkut[grep("leiden.1",Rx),gp:="leiden.1"]
orkut[grep("leiden.01",Rx),gp:="leiden.01"]
orkut[grep("leiden.001",Rx),gp:="leiden.001"]
#
orkut[grep("r2nontree_clusters",Rx),gp2:="r2tree"]
orkut[grep("r2nontree_n10_clusters",Rx),gp2:="r2tree_size"]
orkut[grep("after",Rx),gp2:="cm1"]
#
orkut1 <- orkut[!is.na(gp2),]
orkut2 <- orkut[is.na(gp2),]
orkut2[Rx %like% "leiden.[0-9]+_nontree_clusters.tsv",gp2:='tree']
orkut2[Rx %like% "leiden.[0-9]+_nontree_n10_clusters.tsv",gp2:='tree_size']
orkut2[is.na(gp2),gp2:='leiden']
orkut3 <- rbind(orkut1,orkut2)
orkut3$gp <- factor(orkut3$gp, levels=c('leiden.5','leiden.1','leiden.01','leiden.001'))
orkut3$gp2 <- factor(orkut3$gp2, levels=c('leiden','tree','tree_size','cm1','r2tree','r2tree_size'))
orkut3 <- orkut3[order(gp,gp2)]
#
p_orkut <- ggplot(data=orkut3, aes(x=gp2, y=node_cov)) +  geom_bar(stat="identity", fill="steelblue") + facet_wrap(~ gp) + ylim(0,1)
pdf('orkut.pdf')
print(p_orkut)
dev.off()
p_orkut
orkut
orkut3

# *** wiki-topcats ***
wiki_topcats <- fread('wiki_topcats_cm_df.csv')
# remove cm output before cM-universl treatment
wiki_topcats <- wiki_topcats[grep("preprocessed", wiki_topcats$Rx, invert = TRUE), ]
# wiki_topcats <- wiki_topcats[grep("nontree_clusters", wiki_topcats$Rx, invert = TRUE), ]
t <- sort(wiki_topcats$Rx,decreasing=TRUE)
wiki_topcats$Rx <- factor(wiki_topcats$Rx,levels=t)
wiki_topcats[grep("leiden.5",Rx),gp:="leiden.5"]
wiki_topcats[grep("leiden.1",Rx),gp:="leiden.1"]
wiki_topcats[grep("leiden.01",Rx),gp:="leiden.01"]
wiki_topcats[grep("leiden.001",Rx),gp:="leiden.001"]
#
wiki_topcats[grep("r2nontree_clusters",Rx),gp2:="r2tree"]
wiki_topcats[grep("r2nontree_n10_clusters",Rx),gp2:="r2tree_size"]
wiki_topcats[grep("after",Rx),gp2:="cm1"]
#
wiki_topcats1 <- wiki_topcats[!is.na(gp2),]
wiki_topcats2 <- wiki_topcats[is.na(gp2),]
wiki_topcats2[Rx %like% "leiden.[0-9]+_nontree_clusters.tsv",gp2:='tree']
wiki_topcats2[Rx %like% "leiden.[0-9]+_nontree_n10_clusters.tsv",gp2:='tree_size']
wiki_topcats2[is.na(gp2),gp2:='leiden']
wiki_topcats3 <- rbind(wiki_topcats1,wiki_topcats2)
wiki_topcats3$gp <- factor(wiki_topcats3$gp, levels=c('leiden.5','leiden.1','leiden.01','leiden.001'))
wiki_topcats3$gp2 <- factor(wiki_topcats3$gp2, levels=c('leiden','tree','tree_size','cm1','r2tree','r2tree_size'))
wiki_topcats3 <- wiki_topcats3[order(gp,gp2)]
#
p_wiki_topcats <- ggplot(data=wiki_topcats3, aes(x=gp2, y=node_cov)) +  geom_bar(stat="identity", fill="steelblue") + facet_wrap(~ gp) + ylim(0,1)
pdf('wiki_topcats.pdf')
print(p_wiki_topcats)
dev.off()
p_wiki_topcats
wiki_topcats
wiki_topcats3


# *** lfr_wtp_0.1 ***
lfr_wtp_0.1 <- fread('lfr_wtp_0.1_cm_df.csv')
# remove cm output before cM-universl treatment
lfr_wtp_0.1 <- lfr_wtp_0.1[grep("preprocessed", lfr_wtp_0.1$Rx, invert = TRUE), ]
# lfr_wtp_0.1 <- lfr_wtp_0.1[grep("nontree_clusters", lfr_wtp_0.1$Rx, invert = TRUE), ]
t <- sort(lfr_wtp_0.1$Rx,decreasing=TRUE)
lfr_wtp_0.1$Rx <- factor(lfr_wtp_0.1$Rx,levels=t)
lfr_wtp_0.1[grep("leiden.5",Rx),gp:="leiden.5"]
lfr_wtp_0.1[grep("leiden.1",Rx),gp:="leiden.1"]
lfr_wtp_0.1[grep("leiden.01",Rx),gp:="leiden.01"]
lfr_wtp_0.1[grep("leiden.001",Rx),gp:="leiden.001"]
#
lfr_wtp_0.1[grep("r2nontree_clusters",Rx),gp2:="r2tree"]
lfr_wtp_0.1[grep("r2nontree_n10_clusters",Rx),gp2:="r2tree_size"]
lfr_wtp_0.1[grep("after",Rx),gp2:="cm1"]
#
lfr_wtp_0.11 <- lfr_wtp_0.1[!is.na(gp2),]
lfr_wtp_0.12 <- lfr_wtp_0.1[is.na(gp2),]
lfr_wtp_0.12[Rx %like% "leiden.[0-9]+_nontree_clusters.tsv",gp2:='tree']
lfr_wtp_0.12[Rx %like% "leiden.[0-9]+_nontree_n10_clusters.tsv",gp2:='tree_size']
lfr_wtp_0.12[is.na(gp2),gp2:='leiden']
lfr_wtp_0.13 <- rbind(lfr_wtp_0.11,lfr_wtp_0.12)
lfr_wtp_0.13$gp <- factor(lfr_wtp_0.13$gp, levels=c('leiden.5','leiden.1','leiden.01','leiden.001'))
lfr_wtp_0.13$gp2 <- factor(lfr_wtp_0.13$gp2, levels=c('leiden','tree','tree_size','cm1','r2tree','r2tree_size'))
lfr_wtp_0.13 <- lfr_wtp_0.13[order(gp,gp2)]
#
p_lfr_wtp_0.1 <- ggplot(data=lfr_wtp_0.13, aes(x=gp2, y=node_cov)) +  geom_bar(stat="identity", fill="steelblue") + facet_wrap(~ gp) + ylim(0,1)
pdf('lfr_wtp_0.1.pdf')
print(p_lfr_wtp_0.1)
dev.off()
p_lfr_wtp_0.1
lfr_wtp_0.1
lfr_wtp_0.13


# *** lfr_wtp_0.5 ***
lfr_wtp_0.5 <- fread('lfr_wtp_0.5_cm_df.csv')
# remove cm output before cM-universl treatment
lfr_wtp_0.5 <- lfr_wtp_0.5[grep("preprocessed", lfr_wtp_0.5$Rx, invert = TRUE), ]
# lfr_wtp_0.5 <- lfr_wtp_0.5[grep("nontree_clusters", lfr_wtp_0.5$Rx, invert = TRUE), ]
t <- sort(lfr_wtp_0.5$Rx,decreasing=TRUE)
lfr_wtp_0.5$Rx <- factor(lfr_wtp_0.5$Rx,levels=t)
lfr_wtp_0.5[grep("leiden.5",Rx),gp:="leiden.5"]
lfr_wtp_0.5[grep("leiden.1",Rx),gp:="leiden.1"]
lfr_wtp_0.5[grep("leiden.01",Rx),gp:="leiden.01"]
lfr_wtp_0.5[grep("leiden.001",Rx),gp:="leiden.001"]
#
lfr_wtp_0.5[grep("r2nontree_clusters",Rx),gp2:="r2tree"]
lfr_wtp_0.5[grep("r2nontree_n10_clusters",Rx),gp2:="r2tree_size"]
lfr_wtp_0.5[grep("after",Rx),gp2:="cm1"]
#
lfr_wtp_0.51 <- lfr_wtp_0.5[!is.na(gp2),]
lfr_wtp_0.52 <- lfr_wtp_0.5[is.na(gp2),]
lfr_wtp_0.52[Rx %like% "leiden.[0-9]+_nontree_clusters.tsv",gp2:='tree']
lfr_wtp_0.52[Rx %like% "leiden.[0-9]+_nontree_n10_clusters.tsv",gp2:='tree_size']
lfr_wtp_0.52[is.na(gp2),gp2:='leiden']
lfr_wtp_0.53 <- rbind(lfr_wtp_0.51,lfr_wtp_0.52)
lfr_wtp_0.53$gp <- factor(lfr_wtp_0.53$gp, levels=c('leiden.5','leiden.1','leiden.01','leiden.001'))
lfr_wtp_0.53$gp2 <- factor(lfr_wtp_0.53$gp2, levels=c('leiden','tree','tree_size','cm1','r2tree','r2tree_size'))
lfr_wtp_0.53 <- lfr_wtp_0.53[order(gp,gp2)]
#
p_lfr_wtp_0.5 <- ggplot(data=lfr_wtp_0.53, aes(x=gp2, y=node_cov)) +  geom_bar(stat="identity", fill="steelblue") + facet_wrap(~ gp) + ylim(0,1)
pdf('lfr_wtp_0.5.pdf')
print(p_lfr_wtp_0.5)
dev.off()
p_lfr_wtp_0.5
lfr_wtp_0.5
lfr_wtp_0.53
