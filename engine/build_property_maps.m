function [mu_a_map, mu_t_map, alpha2_map, alpha3_map] = build_property_maps(z_vec, y_vec, ...
        mu_a_bg, mu_t_bg, mu_a_tgt, mu_t_tgt, z_target, r_target, ...
        alpha2_bg, alpha2_tgt, alpha3_bg, alpha3_tgt, y_target)

    if nargin < 10, alpha2_bg  = 0; end
    if nargin < 11, alpha2_tgt = 0; end
    if nargin < 12, alpha3_bg  = 0; end
    if nargin < 13, alpha3_tgt = 0; end
    if nargin < 14, y_target   = 0; end     % lateral target centre [m], default on-axis

    [Z, Y]    = ndgrid(z_vec, y_vec);
    in_target = sqrt((Z - z_target).^2 + (Y - y_target).^2) <= r_target;

    mu_a_map   = mu_a_bg   * ones(length(z_vec), length(y_vec));
    mu_t_map   = mu_t_bg   * ones(length(z_vec), length(y_vec));
    alpha2_map = alpha2_bg * ones(length(z_vec), length(y_vec));
    alpha3_map = alpha3_bg * ones(length(z_vec), length(y_vec));

    mu_a_map(in_target)   = mu_a_tgt;
    mu_t_map(in_target)   = mu_t_tgt;
    alpha2_map(in_target) = alpha2_tgt;
    alpha3_map(in_target) = alpha3_tgt;
end
