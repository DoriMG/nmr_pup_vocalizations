library(ggplot2)
library(patchwork)
library(smplot2)

folder = "data"
out_folder = "figs"

######## Fig S6B - UMAP distance to other colony adults #######
data_file = file.path(folder, "UMAP_distance_development_by_adult.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
df = df[!df$colony=='lannister',] # Don't show Lannister litter
df = df[!df$adult_colony=='boffin',] # Exlude data already shown in main figure
dist_time_by_adult = ggplot(data=df, aes(x=timepoint , y=distance)) +
  geom_point(aes(col=colony, fill=colony))+
  scale_colour_manual(values=c('#edae49', '#d1495b'))+
  sm_statCorr(color='black')+
  facet_wrap(~adult_colony)+
  labs(y ='Distance to colony adults', x='Days postnatal', col='Colony', fill='Colony')+theme_classic()
dist_time_by_adult

######## Fig S6B - UMAP distance to adults of original litter #######
data_file = file.path(folder, "UMAP_distance_development_ori_pups.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
df$animal_ID = factor(df$animal_ID)
df = df[df$timepoint>=59,] # Only show last timepoint and adult

pups_vs_adults = ggplot(data=df, aes(x=colony , y=distance)) +
  geom_point(aes(group=animal_ID))+
  geom_line(aes(group=animal_ID), alpha=0.3)+
  stat_summary(fun=mean, geom='point', alpha=1, size=4) +
  labs(y ='Distance to colony dialect', x='Days postnatal')+theme_classic()
pups_vs_adults

# Linear mixed model
lmm = lmer(distance ~ factor(timepoint) + (1|animal_ID), data =df)
anova(lmm)

######## Fig S6B - UMAP distance within litter #######
data_file = file.path(folder, "UMAP_litter_distance_boffin1_litter.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
df$animal_ID = factor(df$animal_ID)
df = df[df$timepoint>=59,]
df$adult = df$timepoint>59

pups_vs_adults_within = ggplot(data=df, aes(x=adult , y=distance)) +
  geom_point(aes(group=animal_ID))+
  stat_summary(fun=mean, geom='point', alpha=1, size=4) +
  scale_x_discrete(labels=c('Pups', 'Adults'))+
  labs(y ='Distance within litter', x='Days postnatal')+theme_classic()
pups_vs_adults_within

# Linear mixed model
lmm = lmer(distance ~ factor(adult) + (1|animal_ID), data =df)
anova(lmm)

## Create figure

all_plots = (dist_time_by_adult)/(pups_vs_adults|pups_vs_adults_within)+ plot_layout(guides = "collect")+
  plot_annotation(tag_levels = 'A')
all_plots
ggsave(file.path(out_folder,'fig_s6.png'),all_plots, width = 10, height =6)
ggsave(file.path(out_folder,'fig_s6.pdf'),all_plots, width = 10, height =6)
