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
  integrate(\(i) 2 * pirwinhall(x = (2*d*m - i) / (2*m), n = 2*d) * dirwinhall(x = i, n = 2),
            lower = 1,
            upper = 2)$value
}


# Setup --------------------------------------------------------------------
design = tidyr::crossing(d = 1:50,
                         m = c(10,100,1000))
tb = dplyr::mutate(design,
                   p = purrr::pmap_dbl(design, pr_signflip),
                   m = glue("Unif(-{m},{m})"))


# Plot ---------------------------------------------------------------------
gg = ggplot(tb,
            aes(x = d, y = p, color = m)) +
  labs(x     = "Dimensionality of Covariates (d)",
       y     = "Percentage of Parameter Space with\nUnexplained Component Sign Flip",
       color = "Measure on Each\nRegression Parameter") +
  theme_bw(base_size = 22) +
  theme(axis.text       = element_text(color = 'black'),
        legend.position = "inside",
        legend.position.inside = c(0.775, 0.15),
        legend.background = element_rect(colour = "black")) +
  scale_color_viridis_d(end = 0.9) +
  scale_y_continuous(labels = scales::percent) +
  geom_line(linewidth = 2)

ggsave(here('Sections', 'Figures', 'prob_unexplained.pdf'),
       gg, 
       width = 10, height = 8, units = "in")
