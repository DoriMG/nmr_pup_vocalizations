library(ggplot2)
library(patchwork)
library(ggmap)

folder = "data"
out_folder = "figs"

### S Fig 1 - additional features ###
data_file = file.path(folder, "call_features.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
# Exclude timepoints outside of experiment
df=df[df$timepoint<65,] 

zero_crossings = ggplot(data=df, aes_string(x="timepoint" , y="zero_crossings", col='colony', fill='colony')) +
  stat_summary(fun=mean, geom='line', alpha=1) +
  stat_summary(fun.data = mean_se, geom="ribbon", alpha=0.5, colour = NA)+
  scale_colour_manual(values=c('#edae49', '#d1495b','#00798c'))+
  scale_fill_manual(values=c('#edae49', '#d1495b','#00798c'))+
  labs(y ='Zero crossings', x='Days postnatal')+theme_classic()
zero_crossings

bandwidth = ggplot(data=df, aes_string(x="timepoint" , y="bandwidth", col='colony', fill='colony')) +
  stat_summary(fun=mean, geom='line', alpha=1) +
  stat_summary(fun.data = mean_se, geom="ribbon", alpha=0.5, colour = NA)+
  scale_colour_manual(values=c('#edae49', '#d1495b','#00798c'))+
  scale_fill_manual(values=c('#edae49', '#d1495b','#00798c'))+
  labs(y ='Bandwidth (Hz)', x='Days postnatal')+theme_classic()
bandwidth

n_peaks = ggplot(data=df, aes_string(x="timepoint" , y="n_peaks", col='colony', fill='colony')) +
  stat_summary(fun=mean, geom='line', alpha=1) +
  stat_summary(fun.data = mean_se, geom="ribbon", alpha=0.5, colour = NA)+
  scale_colour_manual(values=c('#edae49', '#d1495b','#00798c'))+
  scale_fill_manual(values=c('#edae49', '#d1495b','#00798c'))+
  labs(y ='Mean no harmonic peaks', x='Days postnatal')+theme_classic()
n_peaks



## Make S1 plot
all_plots = (zero_crossings|bandwidth|n_peaks)+ plot_layout(guides = "collect")
all_plots
ggsave(file.path(out_folder,'sfig1_extra_feats.png'),all_plots, width = 13, height =4)
ggsave(file.path(out_folder,'sfig1_extra_feats.pdf'),all_plots, width = 13, height =4)