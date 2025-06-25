library(ggplot2)
library(patchwork)
library(ggmap)

folder = "\\\\gpfs.corp.brain.mpg.de\\bark\\data\\1_projects\\pup_paper\\code\\paper_code\\fig1\\data"
out_folder = "\\\\gpfs.corp.brain.mpg.de\\bark\\data\\1_projects\\pup_paper\\code\\paper_code\\fig1\\figs"

### Fig S4!-G - features ##
data_file = file.path(folder, "call_features_isolate.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
df=df[df$timepoint<65,]

## Features
pitch = ggplot(data=df, aes_string(x="timepoint" , y="pitch", col='colony', fill='colony')) +
  stat_summary(fun=mean, geom='line', alpha=1) +
  stat_summary(fun.data = mean_se, geom="ribbon", alpha=0.5, colour = NA)+
  scale_colour_manual(values=c('#d1495b','#00798c'))+
  scale_fill_manual(values=c('#d1495b','#00798c'))+
  labs(y =' Mean pitch (Hz)', x='Days postnatal')+theme_classic()
pitch

zero_crossings = ggplot(data=df, aes_string(x="timepoint" , y="zero_crossings", col='colony', fill='colony')) +
  stat_summary(fun=mean, geom='line', alpha=1) +
  stat_summary(fun.data = mean_se, geom="ribbon", alpha=0.5, colour = NA)+
  scale_colour_manual(values=c('#d1495b','#00798c'))+
  scale_fill_manual(values=c('#d1495b','#00798c'))+
  labs(y ='Zero crossings', x='Days postnatal')+theme_classic()
zero_crossings

duration = ggplot(data=df, aes_string(x="timepoint" , y="duration", col='colony', fill='colony')) +
  stat_summary(fun=mean, geom='line', alpha=1) +
  stat_summary(fun.data = mean_se, geom="ribbon", alpha=0.5, colour = NA)+
  scale_colour_manual(values=c('#d1495b','#00798c'))+
  scale_fill_manual(values=c( '#d1495b','#00798c'))+
  labs(y ='Duration (s)', x='Days postnatal')+theme_classic()
duration

mean_entropy = ggplot(data=df, aes_string(x="timepoint" , y="mean_entropy", col='colony', fill='colony')) +
  stat_summary(fun=mean, geom='line', alpha=1) +
  stat_summary(fun.data = mean_se, geom="ribbon", alpha=0.5, colour = NA)+
  scale_colour_manual(values=c('#d1495b','#00798c'))+
  scale_fill_manual(values=c( '#d1495b','#00798c'))+
  labs(y ='Mean entropy', x='Days postnatal')+theme_classic()
mean_entropy

voiced_perc = ggplot(data=df, aes_string(x="timepoint" , y="voiced_perc", col='colony', fill='colony')) +
  stat_summary(fun=mean, geom='line', alpha=1) +
  stat_summary(fun.data = mean_se, geom="ribbon", alpha=0.5, colour = NA)+
  scale_colour_manual(values=c('#d1495b','#00798c'))+
  scale_fill_manual(values=c( '#d1495b','#00798c'))+
  labs(y ='Voiced ratio', x='Days postnatal')+theme_classic()
voiced_perc

bandwidth = ggplot(data=df, aes_string(x="timepoint" , y="bandwidth", col='colony', fill='colony')) +
  stat_summary(fun=mean, geom='line', alpha=1) +
  stat_summary(fun.data = mean_se, geom="ribbon", alpha=0.5, colour = NA)+
  scale_colour_manual(values=c('#d1495b','#00798c'))+
  scale_fill_manual(values=c( '#d1495b','#00798c'))+
  labs(y ='Bandwidth (Hz)', x='Days postnatal')+theme_classic()
bandwidth

n_peaks = ggplot(data=df, aes_string(x="timepoint" , y="n_peaks", col='colony', fill='colony')) +
  stat_summary(fun=mean, geom='line', alpha=1) +
  stat_summary(fun.data = mean_se, geom="ribbon", alpha=0.5, colour = NA)+
  scale_colour_manual(values=c('#d1495b','#00798c'))+
  scale_fill_manual(values=c( '#d1495b','#00798c'))+
  labs(y ='Mean no harmonic peaks', x='Days postnatal')+theme_classic()
n_peaks


### Fig S4H-I - vocal usage ##

data_file = file.path(folder, "call_occurence_by_animal_isolate.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
df$perc = df$data*100
df=df[df$day<65,]


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


all_plots = (pitch|duration|voiced_perc|mean_entropy)/
  (zero_crossings|bandwidth|n_peaks|plot_spacer())/
  (occurrence_lannister|occurrence_boffin2)+ plot_layout(guides = "collect", heights =c(1,1,3))+
  plot_annotation(tag_levels = 'A')
all_plots

ggsave(file.path(out_folder,'sfig1_isolate.png'),all_plots, width = 12, height =12)
ggsave(file.path(out_folder,'sfig1_isolate.pdf'),all_plots, width = 12, height =12)