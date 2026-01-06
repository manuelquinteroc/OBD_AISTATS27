# Libraries ---------------------------------------------------------------
library(here)
library(tidyr)
library(dplyr)
library(purrr)
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

pr_signflip = function(d, m) {
  integrate(\(a) 2 * pirwinhall(x = (2*d*m - a) / (2*m), n = 2*d) / (2 * m),
            lower = 0,
            upper = m)$value
}


# Setup --------------------------------------------------------------------
design = tidyr::crossing(d = 1:50,
                         m = c(5,10,20,50))
tb = dplyr::mutate(design,
                   p = purrr::pmap_dbl(design, pr_signflip),
                   m = factor(m))


# Plot ---------------------------------------------------------------------
gg = ggplot(tb,
            aes(x = d, y = p, color = m)) +
  labs(y = "Probability of Unexplained Component Sign Flip",
       color = "M") +
  theme_bw(base_size = 18) +
  geom_line()

ggsave(here('Sections', 'Figures', 'prob_unexplained.pdf'),
       gg, 
       width = 10, height = 8, units = "in")
