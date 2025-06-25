library(ggplot2)
library(patchwork)
library(smplot2)


folder = "data"
out_folder = "figs"

######## Fig S7B - Length over time #######
data_file = file.path(folder, "body_development.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)


length_over_time= ggplot(data=df, aes(x=day, y=body_length)) +
  geom_line( aes(col = factor(pup.ID)), size=1, alpha=0.5)+
  stat_summary(fun=mean, geom='line', alpha=1, size=1.5) +
  labs(y ='Body length (mm)', x='Time (days postnatal)', color='animal ID')+
  theme_classic()
length_over_time

######## Fig S7C - length vs weight #######
length_vs_weight= ggplot(data=df, aes(x=weight, y=body_length)) +
  geom_point(aes(col = factor(pup.ID)))+
  labs(y ='Body length (mm)', x='Weight (g)')+
  sm_statCorr(col='black')+
  theme_classic()
length_vs_weight

######## Fig S7D - relative head width #######
rel_head = ggplot(data=df, aes(x=day, y=rel_head)) +
  geom_line( aes(col = factor(pup.ID)), size=1, alpha=0.5)+
  stat_summary(fun=mean, geom='line', alpha=1, size=1.5) +
  labs(y ='Head width relative to body length', x='Time (days postnatal)', color='animal ID')+
  theme_classic()
rel_head

######## Fig S7E - relative belly width #######
potbelly = ggplot(data=df, aes(x=day, y=potbelly)) +
  geom_line( aes(col = factor(pup.ID)), size=1, alpha=0.5)+
  stat_summary(fun=mean, geom='line', alpha=1, size=1.5) +
  labs(y ='Belly relative to body length', x='Time (days postnatal)', color='animal ID')+
  theme_classic()
potbelly

######## Fig S7F - eye opening weight #######
# load eye opening
data_file = file.path(folder, "eye_opening.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
df$open_bin = df$open>0


# Weight for each eye opening group
eye_opening_weight = ggplot(data=df, aes(x=day, y=weight, col=open_bin, fill=open_bin)) +
  stat_summary(fun=mean, geom='line', alpha=1, size=1.5) +
  stat_summary(fun.data = mean_cl_normal, geom="ribbon", alpha=0.3) +
  scale_color_discrete(breaks=c(FALSE,TRUE),
                       labels=c('Closed', 'Open')) + 
  scale_fill_discrete(breaks=c(FALSE,TRUE),
                      labels=c('Closed', 'Open')) + 
  labs(y ='Weight (g)', x='Time (days postnatal)', col=NULL,fill=NULL)+
  xlim(c(37,44))+
  theme_classic()
eye_opening_weight


# Create plot S7#
all_plots = (plot_spacer|length_over_time|length_vs_weight)/
  (rel_head|potbelly|eye_opening_weight)+plot_layout(guides = "collect")+
  plot_annotation(tag_levels = 'A')
all_plots

ggsave(file.path(output_folder,'sfig7.png'),all_plots, width = 12, height =10*2/3)
ggsave(file.path(output_folder,'sfig7.pdf'),all_plots, width = 12, height =10*2/3)