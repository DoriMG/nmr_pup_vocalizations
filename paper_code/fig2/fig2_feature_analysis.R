library(ggplot2)
library(patchwork)


folder = "data"
out_folder = "figs"

######## Fig 2A - Call type UMAP #######
data_file = file.path(folder, "umap_embedding.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)

umap_ct = ggplot(data=df, aes(x=umap_1, y=umap_2, col = call_type )) +
  geom_point(size=0.5)+
  labs(y ='UMAP 2', x='UMAP 1', col = 'Call type')+
  scale_colour_manual(values=c('#8AC926', '#FFCA3A', '#FF595E', '#6A4C93','#FF924C','#1982C4'))+
  theme_void()
umap_ct

######## Fig 2C - HDBSCAN clusters #######
data_file = file.path(folder, "hdbscan_clusters.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
df$clusters = df$clusters+1
umap_clust = ggplot(data=df, aes(x=umap_1, y=umap_2, col = factor(clusters) )) +
  geom_point(size=0.5)+
  labs(y ='UMAP 2', x='UMAP 1', col = 'Cluster')+
  scale_color_manual(values=c('grey', '#264653', '#2a9d8f', '#e9c46a'))+
  theme_void()
umap_clust

######## Fig 2D Cluster membership #######
data_file = file.path(folder, "clust_vs_call_type.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)

call_type_membership = ggplot(df, aes(x=call_type, y=data, fill=factor(cluster))) + 
  geom_bar(position="fill", stat="identity")+
  labs(x='Call type', y='Cluster membership', fill = 'Cluster')+
  scale_fill_manual(values=c('grey', '#264653', '#2a9d8f', '#e9c46a'))+
  theme_classic()
call_type_membership

######## Fig 2E-F Cluster features #######
data_file = file.path(folder, "hdbscan_clusters.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
df$clusters = df$clusters+1

cluster_duration =  ggplot(data=df, aes(x=factor(clusters)  , y=duration, fill=factor(clusters) )) +
  stat_summary(fun=mean, geom='bar', alpha=1) +
  stat_summary(fun.data = mean_cl_normal, geom="errorbar", alpha=1, width=0.3)+
  scale_fill_manual(values=c('grey', '#264653', '#2a9d8f', '#e9c46a'))+
  labs(y ='Duration (s)', x='Cluster')+theme_classic()
cluster_duration

cluster_voiced =  ggplot(data=df, aes(x=factor(clusters)  , y=voiced_perc, fill=factor(clusters) )) +
  stat_summary(fun=mean, geom='bar', alpha=1) +
  stat_summary(fun.data = mean_cl_normal, geom="errorbar", alpha=1, width=0.3)+
  scale_fill_manual(values=c('grey', '#264653', '#2a9d8f', '#e9c46a'))+
  labs(y ='Voiced ratio', x='Cluster')+theme_classic()
cluster_voiced

######## Fig 2G Typicality analysis #######
data_file = file.path(folder, "membership_by_ct.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
ct_typicality = ggplot(df, aes(x=call_type, y=typicality, fill = call_type)) + 
  geom_boxplot(outlier.colour="black", outlier.shape=16,
               outlier.size=2, notch=FALSE)+
  scale_fill_manual(values=c('#8AC926', '#FFCA3A', '#FF595E', '#6A4C93','#FF924C','#1982C4'))+
  labs(y='Typicality coefficient', x='Call type')+ theme_classic()
ct_typicality

# ANOVA
res.aov <- aov(typicality ~ call_type, data = df)
summary(res.aov)


############## Create figure 2 ##########
layout <- "
AAAABBBB
AAAABBBB
CCCCDDEE
CCCCFFGG

"
all_plots =  plot_spacer()+umap_ct+ umap_clust+
  call_type_membership+cluster_duration+cluster_voiced+
  ct_typicality
  plot_layout(design = layout, guides = "collect")+  plot_annotation(tag_levels = 'A')
all_plots
ggsave(file.path(out_folder,'fig2_call_types.png'),all_plots, width = 24, height =20)
ggsave(file.path(out_folder,'fig2_call_types.pdf'),all_plots, width = 24, height =20)
