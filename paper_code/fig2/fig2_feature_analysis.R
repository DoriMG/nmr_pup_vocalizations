library(ggplot2)
library(patchwork)

folder = "\\\\gpfs.corp.brain.mpg.de\\bark\\data\\1_projects\\pup_paper\\code\\paper_code\\fig2\\data"
out_folder = "\\\\gpfs.corp.brain.mpg.de\\bark\\data\\1_projects\\pup_paper\\code\\paper_code\\fig2\\figs"


data_file = file.path(folder, "umap_embedding.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)

umap_ct = ggplot(data=df, aes(x=umap_1, y=umap_2, col = call_type )) +
  geom_point(size=0.5)+
  labs(y ='UMAP 2', x='UMAP 1', col = 'Call type')+
  scale_colour_manual(values=c('#8AC926', '#FFCA3A', '#FF595E', '#6A4C93','#FF924C','#1982C4'))+
  theme_void()
umap_ct

ggsave(file.path(out_folder,'umap_ct.png'),umap_ct, width = 12, height =10)



data_file = file.path(folder, "hdbscan_clusters.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
df$clusters = df$clusters+1
umap_clust = ggplot(data=df, aes(x=umap_1, y=umap_2, col = factor(clusters) )) +
  geom_point(size=0.5)+
  labs(y ='UMAP 2', x='UMAP 1', col = 'Cluster')+
  scale_color_manual(values=c('grey', '#264653', '#2a9d8f', '#e9c46a'))+
  theme_void()
umap_clust

##
data_file = file.path(folder, "clust_vs_call_type.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)

clust_membership = ggplot(df, aes(fill=call_type, y=data, x=factor(cluster))) + 
  geom_bar(position="fill", stat="identity")+
  labs(y ='Call type membership', x='Cluster', fill = 'Call type')+
  scale_fill_brewer(palette="Set2")+
  theme_classic()
clust_membership


call_type_membership = ggplot(df, aes(x=call_type, y=data, fill=factor(cluster))) + 
  geom_bar(position="fill", stat="identity")+
  labs(x='Call type', y='Cluster membership', fill = 'Cluster')+
  scale_fill_manual(values=c('grey', '#264653', '#2a9d8f', '#e9c46a'))+
  theme_classic()
call_type_membership

## Cluster properties
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


data_file = file.path(folder, "membership_by_ct.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)


ct_typicality = ggplot(df, aes(x=call_type, y=typicality, fill = call_type)) + 
  geom_boxplot(outlier.colour="black", outlier.shape=16,
               outlier.size=2, notch=FALSE)+
  scale_fill_manual(values=c('#8AC926', '#FFCA3A', '#FF595E', '#6A4C93','#FF924C','#1982C4'))+
  labs(y='Typicality coefficient', x='Call type')+ theme_classic()
ct_typicality

res.aov <- aov(typicality ~ call_type, data = df)
# Summary of the analysis
summary(res.aov)

# Combo membership
data_file = file.path(folder, "combo_membership.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
df=df[df$timepoint <65,]

data_mod <- cbind(df[1:5], stack(df[6:7])) 


combo_mem = ggplot(data=data_mod, aes(x=timepoint , y=values, col=ind)) +
  geom_point()+
  geom_smooth()+
  facet_wrap(~colony)+
  labs(y ='Typicality', x='Days postnatal', col='Cluster', fill='Cluster')+theme_classic()
combo_mem

# phee membership
data_file = file.path(folder, "phee_membership.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
df=df[df$timepoint <65,]

data_mod <- cbind(df[1:5], stack(df[6:7])) 


ph_mem = ggplot(data=data_mod, aes(x=timepoint , y=values, col=ind)) +
  geom_point()+
  geom_smooth()+
  facet_wrap(~colony)+
  labs(y ='Typicality', x='Days postnatal', col='Cluster', fill='Cluster')+theme_classic()
ph_mem

layout <- "
AAAABBBB
AAAABBBB
CCCCDDEE
CCCCFFGG
#HHHIII#

"
all_plots =  plot_spacer()+umap_ct+ umap_clust+
  call_type_membership+cluster_duration+cluster_voiced+
  ct_typicality+combo_mem+ph_mem+
  plot_layout(design = layout, guides = "collect")+  plot_annotation(tag_levels = 'A')

all_plots = (random_forest|umap_ct|umap_clust)/
  (call_type_membership|cluster_duration|cluster_voiced)/
  (ct_typicality|combo_mem+plot_layout(widths = c(1, 2)))+ plot_layout(guides = "collect")+
  plot_annotation(tag_levels = 'A')
all_plots
ggsave(file.path(out_folder,'fig2_call_types_v3.png'),all_plots, width = 24, height =24)
ggsave(file.path(out_folder,'fig2_call_types_v3.pdf'),all_plots, width = 24, height =24)
