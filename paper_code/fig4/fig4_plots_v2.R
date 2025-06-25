library(ggplot2)
library("dplyr")
library(smplot2)
library(nls)
library(patchwork)



folder = "data"
out_folder = "figs"


######## Fig 4A - Weight over time #######
data_file = file.path(data_folder, "all_weights.csv")
df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
df = df[df$DateMeasured<65,]

weight_over_time = ggplot(data=df, aes(x=DateMeasured, y=Weight, col=Colony)) +
  geom_line( aes(group = AnimalID), linewidth=1, alpha=0.5)+
  stat_summary(fun=mean, geom='line', alpha=1, size=1.5) +
  labs(y ='Weight (g)', x='Time (days postnatal)')+
  scale_colour_manual(values=c('#edae49', '#d1495b','#00798c'), labels=(c('Boffin','Boffin 2', 'Lannister')))+
  theme_classic()
weight_over_time

######## Fig 4B-C - Weight over time #######
data_file = file.path(data_folder, "all_occ.csv")

df <- read.csv(data_file, header=TRUE, stringsAsFactors=TRUE)
# Convert to % and clean data
df$data = df$data*100
df = df[complete.cases(df), ]
df = df[df$day<65,]
df = df[df$vocal_type == 'sc',]

## Create models
m1 <- nls(data ~ SSlogis(day, Asym, xmid, scal), data = df)
m2 = nls(data ~ SSlogis(weight, Asym, xmid, scal), data = df)

## Make predictions
age_data = data.frame(day=seq(min(df$day), max(df$day), length.out = 1000))
age_data$pred_y= predict(m1, newdata=age_data)

weight_data = data.frame(weight=seq(min(df$weight), max(df$weight), length.out = 1000))
weight_data$pred_y= predict(m2, newdata=weight_data)

######## Fig 4B - SC vs age #######
sc_vs_age=ggplot(data=df, aes(x=day, y=data)) +
  geom_point(aes(col=colony))+
  labs(y ='% Soft chirps', x='Age (days)')+
  geom_line(data=age_data, aes(x=day, y = pred_y), size = 1)+
  scale_colour_manual(values=c('#edae49', '#d1495b','#00798c'), labels=(c('Boffin','Boffin 2', 'Lannister')))+
  theme_classic()
sc_vs_age

######## Fig 4C - SC vs weight #######
sc_vs_weight=ggplot(data=df, aes(x=weight, y=data )) +
  geom_point(aes(col=colony))+
  labs(y ='Body length (mm)', x='Weight (g)')+
  geom_line(data=weight_data, aes(x=weight, y = pred_y), size = 1)+
  scale_colour_manual(values=c('#edae49', '#d1495b','#00798c'), labels=(c('Boffin','Boffin 2', 'Lannister')))+
  theme_classic()
sc_vs_weight

# Create predicitons and put into new dataset
pred_age = abs(df$data-predict(m1, newdata=df))
pred_weight = abs(df$data-predict(m2, newdata=df))

age_data = data.frame(error=pred_age)
age_data$dataset = 1
age_data$animal_id = df$animal_id

weight_data = data.frame(error=pred_weight)
weight_data$dataset = 2
weight_data$animal_id = df$animal_id 

######## Fig 4C- inset #######
df = rbind(age_data, weight_data)

sigmoid_error = ggplot(df, aes(x=as.factor(dataset), y=error)) + 
  geom_boxplot(fill="slateblue", alpha=0.2) +
  labs(y ='Model error', x='Model')+
  scale_x_discrete(labels=c("Age", "Weight"))+
  theme_classic()

t.test(pred_age, pred_weight)
lmm = lmer(error ~ factor(dataset) + (1|animal_id), data =df)
anova(lmm)


### Output figure

all_plots = (weight_over_time|sc_vs_age|sc_vs_weight)/
  (sigmoid_error|plot_spacer()|plot_spacer())+plot_layout(guides = "collect")+
  plot_annotation(tag_levels = 'A')
all_plots

ggsave(file.path(output_folder,'fig4_development.png'),all_plots, width = 12, height =6)
ggsave(file.path(output_folder,'fig4_development.pdf'),all_plots, width = 12, height =6)


