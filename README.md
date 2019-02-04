# Glassdoor-Company-Reviews
This repository will have the scripts and output for a text analytics project on Glassdoor reviews. First, I'll upload all the necessary packages and get the web scraping underway.

```r
library(tidytext)
library(dplyr)
library(stringr)
library(lubridate)
library(ggplot2)
library(anytime)


# Read the data frame in 
df <- read.csv("GD_data.csv", stringsAsFactors = TRUE)

# The dates were giving me hell
date<- df$Date
date1 <- anytime(as.factor(date))

new_df1 <- df %>%
  mutate(reviews = as.character(rev.sum),
         pros = as.character(Pros),
         cons = as.character(Cons),
         status = as.character(Status),
         year = as.integer(rev.year),
         dates = date1)

# There were multiple columns of text. So I included them all rather than just the description
df3 <- within(new_df1, text <- paste(new_df1$reviews, new_df1$pros, new_df1$cons)) 

# Unnest the tokens to prepare for sentiment analysis
tidy_reviews2 <- df3 %>%
  unnest_tokens(word, text) 

tidy_reviews2 %>%
  anti_join(stop_words) %>%
  count(word, sort = TRUE)

tidy_reviews2 %>%
  count(status) %>%
  rename(status_total = n)

# Now for the actual sentiment analysis!!
reviews_sentiment2 <- tidy_reviews2 %>%
  ungroup %>%
  inner_join(get_sentiments("nrc"))

### Here I'll give some visualizations of the text. 

# Top 15 words according to sentiment
reviews_sentiment2 %>%
  count(word, sentiment) %>%
  group_by(sentiment) %>%
  top_n(15, n) %>%
  ungroup() %>%
  mutate(word = reorder(word, n)) %>%
  ggplot(aes(word, n, fill = sentiment)) +
  geom_col(show.legend = FALSE) +
  facet_wrap(~ sentiment, scales = "free") +
  coord_flip() + 
  ggtitle("Top Fifteen Words according to Sentiment")



# Group by current and former employees
reviews_sentiment2 %>%
  filter(sentiment == "negative") %>%
  count(word, status) %>%
  group_by(status) %>%
  top_n(10, n) %>%
  ungroup() %>%
  mutate(word = reorder(paste(word, status, sep = "__"), n)) %>%
  # Set up the plot with aes()
  ggplot(aes(word, n, fill = status)) +
  geom_col(show.legend = FALSE) +
  scale_x_discrete(labels = function(x) gsub("__.+$", "", x)) +
  facet_wrap(~ status, nrow = 2, scales = "free") +
  coord_flip()

# Together. Forget about grouping 
reviews_sentiment2 %>%
  filter(sentiment == "negative") %>%
  count(word, status) %>%
  top_n(15, n) %>%
  ungroup() %>%
  mutate(word = reorder(paste(word, status, sep = "__"), n)) %>%
  # Set up the plot with aes()
  ggplot(aes(word, n, fill = status)) +
  geom_col(show.legend = FALSE) +
  scale_x_discrete(labels = function(x) gsub("__.+$", "", x)) +
  coord_flip()

### Maybe some wordclouds would look nice!!?
library("tm")
library("SnowballC")
library("wordcloud")
library("RColorBrewer")

negative <- reviews_sentiment2 %>% ## First done by negative 
  filter(sentiment %in% c("negative", "anger", "fear"))

wordcloud(words = negative$word, min.freq = 3, 
          res = 300,
          max.words = 200, random.order=FALSE, rot.per= .25, 
          colors=brewer.pal(8, "Dark2")) 


# Now by positive
dropwords <- c("favoritism", "good", "work", "working", "management","bureaucracy") 

positive <- reviews_sentiment2 %>%
  filter(sentiment %in% c("positive", "joy", "trust")) %>%
  filter(!word %in% dropwords)

wordcloud(words = positive$word, min.freq = 3, res = 300,
          max.words = 200, random.order=FALSE, rot.per= .25, 
          colors=brewer.pal(8, "Dark2"))


# How about looking at the distribution of sentiment reviews over time?

sentiment_by_time <- tidy_reviews2 %>% ## Creating the variable 
  mutate(date = floor_date(dates, unit = "1 month")) %>%
  group_by(dates) %>%
  mutate(total_words = n()) %>%
  ungroup() %>%
  inner_join(get_sentiments("bing"))


sentiment_by_time %>% 
  # Filter for positive and negative words
  filter(sentiment %in% c("positive", "negative", "joy", "trust", "anger", "fear")) %>%
  # Count by date, sentiment, and total_words
  count(date, sentiment, total_words) %>%
  ungroup() %>%
  mutate(percent = n / total_words) %>%
  # Set up the plot with aes()
  ggplot(aes(date, log10(percent), color = sentiment)) +
  geom_line(size = 0.75) +
  geom_smooth(method = "lm", se = FALSE, lty = 2) +
  expand_limits(y = 0) +
  ggtitle("Distribution of positive and negative sentiment reviews over time") +
  theme(plot.title = element_text(size = 18, hjust = 0.5))

# Now for some Boxplots  betweeen negative and positive
sentiment_by_time %>%
  filter(sentiment %in% c("negative", "anger", "fear")) %>%
  count(word, year, total_words) %>% 
  ungroup() %>%
  mutate(percent = n / total_words) %>%
  # Use ggplot to set up a plot with year and percent
  ggplot(aes(as.factor(year), percent)) +
  geom_boxplot()

sentiment_by_time %>%
  filter(sentiment %in% c("positive", "joy", "trust")) %>%
  count(word, year, total_words) %>% 
  ungroup() %>%
  mutate(percent = n / total_words) %>%
  # Use ggplot to set up a plot with year and percent
  ggplot(aes(as.factor(year), percent)) +
  geom_boxplot()


## Do a linear regression looking at how positive and negative sentiment 
## are related to date. 

# First by negative sentiment
negative_by_year <- sentiment_by_time %>%
  filter(sentiment %in% c("negative", "anger", "fear")) %>%
  count(word, date, total_words) %>%
  ungroup() %>%
  mutate(percent = n / total_words)

model_negative <- lm(percent ~ date, data = negative_by_year)

ggplot(negative_by_year, aes(x = date, y = log10(percent))) + 
  geom_point(alpha = 1/10, size = 2) +
  geom_smooth(method = "lm", se = TRUE, color = "red") +
  expand_limits(y = 0) +
  ggtitle("Percent of negative sentiment reviews over time") +
  theme(plot.title = element_text(size = 18, hjust = 0.5))


# Now for positive comments
positive_by_year <- sentiment_by_time %>%
  filter(sentiment %in% c("positive", "joy", "trust")) %>%
  count(word, date, total_words) %>%
  ungroup() %>%
  mutate(percent = n / total_words)

model_positive <- lm(percent ~ date, data = positive_by_year)

ggplot(positive_by_year, aes(x = date, y = log10(percent))) + 
  geom_point(alpha = 1/10, size = 2) +
  geom_smooth(method = "lm", se = TRUE, color = "red") +
  expand_limits(y = 0) +
  ggtitle("Percent of positive sentiment reviews over time") +
  theme(plot.title = element_text(size = 18, hjust = 0.5))


sent_overall <- sentiment_by_time %>%
  filter(sentiment %in% c("positive", "negative", "joy", "trust", "anger", "fear")) %>%
  count(word, date, total_words, sentiment) %>%
  ungroup() %>%
  mutate(percent = n / total_words)

# Looks amazing together using faceted grid!!
ggplot(sent_overall, aes(x = date, y = log10(percent))) + 
  geom_point(alpha = 1/10, size = 2) +
  geom_smooth(method = "lm", se = TRUE, color = "red") +
  expand_limits(y = 0) +
  facet_wrap(~ sentiment) +
  ggtitle("Percent of positive and negative sentiment reviews over time") +
  theme(plot.title = element_text(size = 18, hjust = 0.5))


# See if any of the words change over time
tidy_reviews2 %>%
  # Define a new column that rounds each date to the nearest 1 month
  mutate(date = floor_date(dates, unit = "1 month")) %>%
  filter(word %in% c("lack", "difficult", "hard", "horrible",
                     "bad")) %>%
  # Count by date and word
  count(date, word) %>%
  ungroup() %>%
  # Set up your plot with aes()
  ggplot(aes(date, n, color = word)) +
  # Make facets by word
  facet_wrap(~ word) +
  geom_line(size = 1.5, show.legend = FALSE) +
  ylim(0, 5) + expand_limits(y = 0)
```

