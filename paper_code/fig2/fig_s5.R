library(ggplot2)
library(patchwork)

folder = "data"
out_folder = "figs"

############### Fig S5A Feature correlations ####################
data_file = file.path(folder, "feat_correlation.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)


feat_correlations = ggplot(df, aes(x=feat1, y=feat2, fill=data)) +
  geom_tile(aes(fill = data))+
  scale_fill_gradient2(low = '#009fb7', mid = "white", high = "#fe4a49", limits=c(-1,1))+theme_classic()+
  labs(y ='Features', x='Features', fill="Spearman's correlation")+
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1))

feat_correlations

############### Fig S5B Random Forest ####################
data_file = file.path(folder, "random_forest.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)

random_forest = ggplot(df, aes(x=true, y=predicted, fill=data)) +
  geom_tile(aes(fill = data))+
  scale_fill_gradient(low = "white", high = "#0b5351", limits=c(0,1))+theme_classic()+
  labs(y ='Predicted type', x='True type', fill=NULL)+
  geom_text(aes(label = round(data,2)), color = "black", size = 4)

random_forest

############### Fig S5C Silhouette scores ####################
data_file = file.path(folder, "sil_scores.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)


sil_score = ggplot(df, aes(x=factor(min_sample), y=factor(min_cluster), fill=data)) +
  geom_tile(aes(fill = data))+
  scale_fill_gradient2(low = '#009fb7', mid = "white", high = "#fe4a49", limits=c(-0.35,0.35))+theme_classic()+
  labs(x ='Min sample', y='Min cluster', fill="Silhouette score")

sil_score

############### Fig S5 D-F cluster usage ####################
data_file = file.path(folder, "clust_occ_by_animal.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
df$perc = df$data*100
df=df[df$day<65,]
df$vocal_type = df$vocal_type+1 # Cluster indexing in Python starts with -1

df_temp = df[df$colony=='boffin',]
occurrence_boffin = ggplot(df_temp, aes(y=vocal_type, x=factor(day), fill=perc)) +
  geom_tile(aes(fill = perc))+
  scale_fill_gradient(low = "white", high = "#edae49", limits=c(0,100))+theme_classic()+
  labs(x ='Days postnatal', y='Cluster', fill="Occurrence (%)")+ggtitle('Boffin')
occurrence_boffin

df_temp = df[df$colony=='lannister',]
occurrence_lannister= ggplot(df_temp, aes(y=vocal_type, x=factor(day), fill=perc)) +
  geom_tile(aes(fill = perc))+
  scale_fill_gradient(low = "white", high = "#00798c", limits=c(0,100))+theme_classic()+
  labs(x ='Days postnatal', y='Cluster', fill="Occurrence (%)")+ggtitle('Lannister')
occurrence_lannister


df_temp = df[df$colony=='boffin_2',]
occurrence_boffin2 = ggplot(df_temp, aes(y=vocal_type, x=factor(day), fill=perc)) +
  geom_tile(aes(fill = perc))+
  scale_fill_gradient(low = "white", high = "#d1495b", limits=c(0,100))+theme_classic()+
  labs(x ='Days postnatal', y='Cluster', fill="Occurrence (%)")+ggtitle('Boffin 2')
occurrence_boffin2


############## Create figure S5 ##########
all_plots = (feat_correlations|random_forest|sil_score)/
  occurrence_boffin/occurrence_lannister/occurrence_boffin2+plot_layout(guides = "collect",heights = c(2.3,1,1,1))+
  plot_annotation(tag_levels = 'A')
all_plots
ggsave(file.path(out_folder,'fig_s5.png'),all_plots, width = 20, height =15)
ggsave(file.path(out_folder,'fig_s5.pdf'),all_plots, width = 20, height =15)

