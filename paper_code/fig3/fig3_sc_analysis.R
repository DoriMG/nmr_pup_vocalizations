library(ggplot2)
library(patchwork)
library(smplot2)



folder = "data"
out_folder = "figs"

######## Fig 3A - UMAP #######
data_file = file.path(folder, "umap_embedding.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
df$animal_id = factor(df$animal_id)

umap_id = ggplot(data=df, aes(x=umap_1, y=umap_2, col = colony )) +
  geom_point(size=0.5)+
  scale_colour_manual(values=c('#edae49', '#d1495b',"black",'#00798c','#A1CCA5', '#A96DA3'))+
  labs(y ='UMAP 2', x='UMAP 1', col = 'Colony')+
  theme_void()
umap_id


######## Fig 3B - Euclidean distance over time #######
data_file = file.path(folder, "UMAP_distance_development.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
df = df[!df$colony=='lannister',]
dist_time = ggplot(data=df, aes(x=timepoint , y=distance)) +
  geom_point(aes(col=colony, fill=colony))+
  scale_colour_manual(values=c('#edae49', '#d1495b'))+
  sm_statCorr(color='black')+
  labs(y ='Distance to colony adults', x='Days postnatal', col='Colony', fill='Colony')+theme_classic()
dist_time

######## Fig 3B - Euclidean distance within litter over time #######
data_file = file.path(folder, "UMAP_litter_distance.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)

litter_distance = ggplot(data=df, aes(x=timepoint , y=distance, col=colony)) +
  geom_point()+
  sm_statCorr()+
  scale_color_manual(values=c('#332D56', '#71C0BB'), labels=c('Between litters', 'Within litter'))+
  labs(y ='Distance between individuals', x='Days postnatal', col=NULL, fill=NULL)+theme_classic()
litter_distance

### Output figure
all_plots = ((umap_id|(dist_time/litter_distance))) +plot_layout(guides = "collect")+
  plot_annotation(tag_levels = 'A')
all_plots
ggsave(file.path(out_folder,'fig3_soft_chirps.png'),all_plots, width = 12, height =12)
ggsave(file.path(out_folder,'fig3_soft_chirps.pdf'),all_plots, width = 12, height =12)



