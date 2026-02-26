function I_map = build_intensity_map(beam, z_vec, y_vec, I_surface_peak, mu_t_map)
    z_points = length(z_vec);
    y_points = length(y_vec);
    dz       = z_vec(2) - z_vec(1);

    if nargin < 5 || isempty(mu_t_map)
        mu_t_map = zeros(z_points, y_points);
    end

    I_map = zeros(z_points, y_points);
    accumulated_att = 0;

    for iz = 1:z_points
        delta_z      = z_vec(iz) - beam.z_focus;
        w_z          = beam.w0 * sqrt(1 + (delta_z / beam.zR)^2);

        I_row        = (beam.w_surface / w_z)^2 * exp(-2 * y_vec.^2 / w_z^2);
        I_map(iz, :) = I_surface_peak * I_row * exp(-accumulated_att);

        if iz < z_points
            I_cur    = I_map(iz, :);
            avg_mu_t = sum(mu_t_map(iz,:) .* I_cur) / sum(I_cur);
            accumulated_att = accumulated_att + avg_mu_t * dz;
        end
    end
end
