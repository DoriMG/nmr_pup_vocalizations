library(ggplot2)
library(patchwork)
library(ggmap)

folder = "\\\\gpfs.corp.brain.mpg.de\\bark\\data\\1_projects\\pup_paper\\code\\paper_code\\fig1\\data"
out_folder = "\\\\gpfs.corp.brain.mpg.de\\bark\\data\\1_projects\\pup_paper\\code\\paper_code\\fig1\\figs"


data_file = file.path(folder, "call_occurence_by_animal.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
df$perc = df$data*100
# Exclude timepoints outside of experiment
df=df[df$day<65,]

df_temp = df[df$colony=='boffin',]
# Exclude animals which did not complete experiment
df_temp = df_temp[df_temp$animal_id !='0000',]
occurrence_by_id_boffin = ggplot(df_temp, aes(x=vocal_type, y=factor(day), fill=perc)) +
  geom_tile(aes(fill = perc))+
  scale_fill_gradient(low = "white", high = "#edae49", limits=c(0,100))+theme_classic()+
  labs(y ='Days postnatal', x='Call type', fill="Occurrence (%)")+
  facet_wrap(~animal_id, ncol=4)+
  ggtitle('Boffin')
occurrence_by_id_boffin


df_temp = df[df$colony=='lannister',]
# Exclude animals which did not complete experiment
df_temp = df_temp[df_temp$animal_id !='5912',]
df_temp = df_temp[df_temp$animal_id !='5916',]
df_temp = df_temp[df_temp$animal_id !='na',]
occurrence_by_id_lan = ggplot(df_temp, aes(x=vocal_type, y=factor(day), fill=perc)) +
  geom_tile(aes(fill = perc))+
  scale_fill_gradient(low = "white", high = "#00798c", limits=c(0,100))+theme_classic()+
  labs(y ='Days postnatal', x='Call type', fill="Occurrence (%)")+
  facet_wrap(~animal_id, ncol=4)+
  ggtitle('Lannister')
occurrence_by_id_lan


df_temp = df[df$colony=='boffin_2',]
# Exclude animals which did not complete experiment
df_temp = df_temp[df_temp$animal_id !='0410',]
df_temp = df_temp[df_temp$animal_id !='0414',]
df_temp = df_temp[df_temp$animal_id !='0418',]
occurrence_by_id_boffin2 = ggplot(df_temp, aes(x=vocal_type, y=factor(day), fill=perc)) +
  geom_tile(aes(fill = perc))+
  scale_fill_gradient(low = "white", high = "#d1495b", limits=c(0,100))+theme_classic()+
  labs(y ='Days postnatal', x='Call type', fill="Occurrence (%)")+
  facet_wrap(~animal_id, ncol=4)+
  ggtitle('Boffin 2')
occurrence_by_id_boffin2

all_plots = (occurrence_by_id_boffin/occurrence_by_id_lan/occurrence_by_id_boffin2)+ plot_layout(guides = "collect")+
  plot_annotation(tag_levels = 'A')
all_plots
ggsave(file.path(out_folder,'sfig1_individual_occ.png'),all_plots, width = 12, height =18)
ggsave(file.path(out_folder,'sfig1_individual_occ.pdf'),all_plots, width = 12, height =18)
