r_mu = function(n, d, M) {
  matrix(runif(n * d, min = -1 * M, max = M),
         nrow = d, ncol = n)
}

r_deltabeta = function(n, d, M) {
  matrix(runif(n * d, min = -1 * M, max = M) - runif(n * d, min = -1 * M, max = M),
         nrow = d, ncol = n)
}

r_deltaalpha = function(n, M) {
  runif(n, min = -1 * M, max = M) - runif(n, min = -1 * M, max = M)
}

pct_explained_montecarlo = function(n_sims, n_covariates, M) {
  mu_h        = r_mu(n = n_sims, d = n_covariates, M = M)
  mu_k        = r_mu(n = n_sims, d = n_covariates, M = M)
  delta_beta  = r_deltabeta(n = n_sims, d = n_covariates, M = M)
  
  mu_h_delta_beta = as.numeric(crossprod(mu_h, delta_beta))
  mu_k_delta_beta = as.numeric(crossprod(mu_k, delta_beta))
  
  mean(sign(mu_h_delta_beta) == sign(mu_k_delta_beta))
}

pct_unexplained_montecarlo = function(n_sims, n_covariates, M) {
  mu_h        = r_mu(n = n_sims, d = n_covariates, M = M)
  mu_k        = r_mu(n = n_sims, d = n_covariates, M = M)
  delta_beta  = r_deltabeta(n = n_sims, d = n_covariates, M = M)
  delta_alpha = r_deltaalpha(n = n_sims, M = M)
  
  mu_h_delta_beta = as.numeric(crossprod(mu_h, delta_beta))
  mu_k_delta_beta = as.numeric(crossprod(mu_k, delta_beta))
  
  min_mtb = pmin(mu_h_delta_beta, mu_k_delta_beta)
  max_mtb = pmax(mu_h_delta_beta, mu_k_delta_beta)
  
  flip = (min_mtb < (-1 * delta_alpha)) & ((-1 * delta_alpha) < max_mtb)
  
  mean(flip)
}

set.seed(1)

library(here)
library(tidyr)
library(dplyr)
library(ggplot2)
library(purrr)

tb = crossing(n_covariates = 1:100,
              M = c(1, 10, 100))

gg_tb = mutate(tb,
               pct_explained   = pmap_dbl(tb, pct_explained_montecarlo, n_sims = 1000),
               pct_unexplained = pmap_dbl(tb, pct_unexplained_montecarlo, n_sims = 1000)) |> 
  pivot_longer(c(pct_explained, pct_unexplained),
               names_to  = "component",
               values_to = "p",
               names_prefix = "pct_") |> 
  mutate(component = ifelse(component == 'explained',
                            'Explained Component',
                            'Unexplained Component'))

gg = ggplot(gg_tb,
       aes(x = n_covariates,
           y = p,
           color = factor(2*M))) +
  facet_grid(cols = vars(component)) +
  labs(x = "Dimensionality of Covariates (d)",
       y = "Percentage of Parameter Space\nWith Sign Flip",
       color = "Cube Side Length (2M)") +
  theme_bw(base_size = 18) +
  theme(axis.text       = element_text(color = 'black'),
        strip.background = element_rect(color = 'black', fill = NA),
        legend.position = "inside",
        legend.position.inside = c(0.25, 0.2),
        legend.background = element_rect(color = "black")) +
  scale_color_viridis_d(option = "rocket", 
                        end = 0.9) +
  scale_y_continuous(labels = scales::percent) +
  geom_line(linewidth = 1.5)
gg

ggsave(here('Sections', 'Figures', 'prob_flip_simulated.pdf'),
       gg, 
       width = 8, height = 5, units = "in")
