# Libraries ---------------------------------------------------------------
library(here)
library(tidyr)
library(dplyr)
library(purrr)
library(glue)
library(ggplot2)

# Helpers -----------------------------------------------------------------
pirwinhall = function(x, n) {
  if (n > 50) {
    pirwinhall_approx(x, n)
  } else {
    pirwinhall_exact(x, n)
  }
}

pirwinhall_exact = function(x, n) {
  
  sapply(x, 
         \(xx) {
           k = seq(0, floor(xx))
           sum((-1)**k * choose(n, k) * (xx - k)**n) / factorial(n)
         })
}

pirwinhall_approx = function(x, n) {
  pnorm(x, mean = n / 2, sd = sqrt(n / 12))
}

dirwinhall = function(x, n) {
  if (n > 50) {
    dirwinhall_approx(x, n)
  } else {
    dirwinhall_exact(x, n)
  }
}

dirwinhall_exact = function(x, n) {
  
  sapply(x, 
         \(xx) {
           k = seq(0, floor(xx))
           sum((-1)**k * choose(n, k) * (xx - k)**{n-1}) / factorial(n-1)
         })
}

dirwinhall_approx = function(x, n) {
  dnorm(x, mean = n / 2, sd = sqrt(n / 12))
}


pr_signflip = function(d, m) {
  
  lower = integrate(\(i) (1 - pirwinhall(x = d + 1 - i, n = 2*d)) * dirwinhall(x = i, n = 2),
                    lower = 0,
                    upper = 1)$value
  
  upper = integrate(\(i) pirwinhall(x = d + 1 - i, n = 2*d) * dirwinhall(x = i, n = 2),
                    lower = 1,
                    upper = 2)$value
  
  lower + upper
}


# Setup --------------------------------------------------------------------
design = tidyr::crossing(d = 1:100,
                         m = 10)
tb = dplyr::mutate(design,
                   pr_unexplained = purrr::pmap_dbl(design, pr_signflip),
                   pr_explained   = 0.5) |> 
  pivot_longer(c(pr_explained, pr_unexplained),
               names_prefix = 'pr_',
               names_to = 'component',
               values_to = 'pr') |> 
  mutate(component = ifelse(component == 'explained',
                            'Explained Component',
                            'Unexplained Component'))


# Plot ---------------------------------------------------------------------
gg = ggplot(tb,
            aes(x = d, y = pr, color = component)) +
  labs(x     = "Dimensionality of Covariates (d)",
       y     = "Percentage of Parameter Space",
       color = "Sign Flip in...") +
  theme_bw(base_size = 26) +
  theme(axis.text       = element_text(color = 'black'),
        legend.position = "inside",
        legend.position.inside = c(0.775, 0.15),
        legend.background = element_rect(colour = "black")) +
  scale_color_manual(values = c('Explained Component'   = '#785EF0',
                                'Unexplained Component' = '#FE6100')) +
  scale_y_continuous(labels = scales::percent) +
  geom_line(linewidth = 2)

ggsave(here('Sections', 'Figures', 'prob_unexplained.pdf'),
       gg, 
       width = 11, height = 8, units = "in")
