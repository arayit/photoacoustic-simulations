function beam = gaussian_beam_params(lambda, NA, n, z_focus)
    beam.lambda   = lambda;
    beam.NA       = NA;
    beam.n        = n;
    beam.z_focus  = z_focus;
    beam.w0       = lambda / (pi * NA);
    beam.zR       = pi * beam.w0^2 * n / lambda;
    beam.w_surface = beam.w0 * sqrt(1 + (z_focus / beam.zR)^2);
end
