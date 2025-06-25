library(ggplot2)
library(patchwork)
library(ggmap)

folder = "data"
out_folder = "figs"

### Fig 1C-F - features ##
data_file = file.path(folder, "call_features.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
# Exclude timepoints outside of experiment
df=df[df$timepoint<65,] 

pitch = ggplot(data=df, aes_string(x="timepoint" , y="pitch", col='colony', fill='colony')) +
  stat_summary(fun=mean, geom='line', alpha=1) +
  stat_summary(fun.data = mean_se, geom="ribbon", alpha=0.5, colour = NA)+
  scale_colour_manual(values=c('#edae49', '#d1495b','#00798c'))+
  scale_fill_manual(values=c('#edae49', '#d1495b','#00798c'))+
  labs(y =' Mean pitch (Hz)', x='Days postnatal')+theme_classic()
pitch

duration = ggplot(data=df, aes_string(x="timepoint" , y="duration", col='colony', fill='colony')) +
  stat_summary(fun=mean, geom='line', alpha=1) +
  stat_summary(fun.data = mean_se, geom="ribbon", alpha=0.5, colour = NA)+
  scale_colour_manual(values=c('#edae49', '#d1495b','#00798c'))+
  scale_fill_manual(values=c('#edae49', '#d1495b','#00798c'))+
  labs(y ='Duration (s)', x='Days postnatal')+theme_classic()
duration

mean_entropy = ggplot(data=df, aes_string(x="timepoint" , y="mean_entropy", col='colony', fill='colony')) +
  stat_summary(fun=mean, geom='line', alpha=1) +
  stat_summary(fun.data = mean_se, geom="ribbon", alpha=0.5, colour = NA)+
  scale_colour_manual(values=c('#edae49', '#d1495b','#00798c'))+
  scale_fill_manual(values=c('#edae49', '#d1495b','#00798c'))+
  labs(y ='Mean entropy', x='Days postnatal')+theme_classic()
mean_entropy

voiced_perc = ggplot(data=df, aes_string(x="timepoint" , y="voiced_perc", col='colony', fill='colony')) +
  stat_summary(fun=mean, geom='line', alpha=1) +
  stat_summary(fun.data = mean_se, geom="ribbon", alpha=0.5, colour = NA)+
  scale_colour_manual(values=c('#edae49', '#d1495b','#00798c'))+
  scale_fill_manual(values=c('#edae49', '#d1495b','#00798c'))+
  labs(y ='Voiced ratio', x='Days postnatal')+theme_classic()
voiced_perc

### Fig 1L-N - vocal usage ##

data_file = file.path(folder, "call_occurence_by_animal.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
df$perc = df$data*100
df=df[df$day<65,]

df_temp = df[df$colony=='boffin',]
occurrence_boffin = ggplot(df_temp, aes(x=vocal_type, y=factor(day), fill=perc)) +
  geom_tile(aes(fill = perc))+
  scale_fill_gradient(low = "white", high = "#edae49", limits=c(0,100))+theme_classic()+
  labs(y ='Days postnatal', x='Call type', fill="Occurrence (%)")+ggtitle('Boffin')
occurrence_boffin

df_temp = df[df$colony=='lannister',]
occurrence_lannister= ggplot(df_temp, aes(x=vocal_type, y=factor(day), fill=perc)) +
  geom_tile(aes(fill = perc))+
  scale_fill_gradient(low = "white", high = "#00798c", limits=c(0,100))+theme_classic()+
  labs(y ='Days postnatal', x='Call type', fill="Occurrence (%)")+ggtitle('Lannister')
occurrence_lannister


df_temp = df[df$colony=='boffin_2',]
occurrence_boffin2 = ggplot(df_temp, aes(x=vocal_type, y=factor(day), fill=perc)) +
  geom_tile(aes(fill = perc))+
  scale_fill_gradient(low = "white", high = "#d1495b", limits=c(0,100))+theme_classic()+
  labs(y ='Days postnatal', x='Call type', fill="Occurrence (%)")+ggtitle('Boffin 2')
occurrence_boffin2


# Make Fig 1

all_plots = (pitch|duration|voiced_perc|mean_entropy)/
  (occurrence_boffin|occurrence_lannister|occurrence_boffin2)+ plot_layout(guides = "collect", heights =c(1,2))+
  plot_annotation(tag_levels = 'A')
ggsave(file.path(out_folder,'fig1.png'),all_plots, width = 16, height =10)
ggsave(file.path(out_folder,'fig1.pdf'),all_plots, width = 16, height =10)



