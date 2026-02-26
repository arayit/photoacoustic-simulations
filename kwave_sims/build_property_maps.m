function [mu_a_map, mu_t_map] = build_property_maps(z_vec, y_vec, ...
        mu_a_bg, mu_t_bg, mu_a_tgt, mu_t_tgt, z_target, r_target)

    [Z, Y]   = ndgrid(z_vec, y_vec);
    in_target = sqrt((Z - z_target).^2 + Y.^2) <= r_target;

    mu_a_map = mu_a_bg * ones(length(z_vec), length(y_vec));
    mu_t_map = mu_t_bg * ones(length(z_vec), length(y_vec));

    mu_a_map(in_target) = mu_a_tgt;
    mu_t_map(in_target) = mu_t_tgt;
end
