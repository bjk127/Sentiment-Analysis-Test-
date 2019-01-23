# Glassdoor-Company-Reviews
This repository will have the scripts and output for a text analytics project on Glassdoor reviews. First, I'll upload all the necessary packages and get the web scraping underway.

library(rvest)
library(purrr)
library(xml2)


baseurl <- "https://www.glassdoor.com/Reviews/"
company <- "Dow-Jones-Reviews-E208"
sort <- ".htm?sort.sortType=RD&sort.ascending=true"

totalreviews <- read_html(paste(baseurl, company, sort, sep="")) %>% 
  html_nodes(".margBot.minor") %>% 
  html_text() %>% 
  sub(" reviews", "", .) %>% 
  sub(",", "", .) %>% 
  as.integer()

maxresults <- as.integer(ceiling(totalreviews/10))    #10 reviews per page, round up to whole number

# Scraping function to create dataframe of: Date, Summary, Rating, Title, Pros, Cons, Helpful
df <- map_df(1:maxresults, function(i) {
  
  Sys.sleep(sample(seq(1, 5, by=0.01), 1))   
  
  cat("boom! ")   #progress indicator
  
  pg <- read_html(paste(baseurl, company, "_P", i, sort, sep=""))   #pagination (_P1 to _P163)
  
  data.frame(rev.date = html_text(html_nodes(pg, ".date.subtle.small, .featuredFlag")),
             rev.sum = html_text(html_nodes(pg, ".reviewLink .summary:not([class*='hidden'])")),
             rev.rating = html_attr(html_nodes(pg, ".gdStars.gdRatings.sm .rating .value-title"), "title"),
             rev.title = html_text(html_nodes(pg, "#ReviewsFeed .hideHH")),
             rev.pros = html_text(html_nodes(pg, "#ReviewsFeed .pros:not([class*='hidden'])")),
             rev.cons = html_text(html_nodes(pg, "#ReviewsFeed .cons:not([class*='hidden'])")),
             rev.helpf = html_text(html_nodes(pg, ".tight")),
             stringsAsFactors=F)
})

#### REGEX ####
# Packages
library(stringr)    #pattern matching functions

# Clean: Helpful
df$rev.helpf <- as.numeric(gsub("\\D", "", df$rev.helpf))

# Add: ID
df$rev.id <- as.numeric(rownames(df))

# Extract: Year, Position, Location, Status
df$rev.year <- as.numeric(sub(".*, ","", df$rev.date))

df$rev.pos <- sub(".* Employee - ", "", df$rev.title)
df$rev.pos <- sub(" in .*", "", df$rev.pos)

df$rev.loc <- sub(".*\\ in ", "", df$rev.title)
df$rev.loc <- ifelse(df$rev.loc %in% 
                       (grep("Former Employee|Current Employee", df$rev.loc, value = T)), 
                     "Not Given", df$rev.loc)

df$rev.stat <- str_extract(df$rev.title, ".* Employee -")
df$rev.stat <- sub(" Employee -", "", df$rev.stat)


write.csv(df, "rvest-scrape-glassdoor-output.csv")
