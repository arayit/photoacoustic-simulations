function [I_map, acc_att_vec] = build_intensity_map(beam, z_vec, y_vec, I_surface_peak, mu_t_map, beam_y_center)
% BUILD_INTENSITY_MAP  Ballistic-photon Beer-Lambert intensity field.
%
%   Computes the 2D intensity map for a focused Gaussian beam propagating
%   through an attenuating medium.  Only ballistic (unscattered) photons
%   are retained: mu_t = mu_a + mu_s uses the FULL scattering coefficient,
%   so every scattered photon is treated as lost from the beam.
%
%   Attenuation is accumulated row-by-row (marching in z) using an
%   intensity-weighted average mu_t per row.  The lateral Gaussian profile
%   shape is preserved; only its amplitude decays with depth.

    z_points = length(z_vec);
    y_points = length(y_vec);
    dz       = z_vec(2) - z_vec(1);

    if nargin < 5 || isempty(mu_t_map)
        mu_t_map = zeros(z_points, y_points);
    end
    if nargin < 6 || isempty(beam_y_center)
        beam_y_center = 0;          % beam axis lateral offset [m], default on-axis
    end

    I_map       = zeros(z_points, y_points);
    acc_att_vec = zeros(z_points, 1);
    accumulated_att = 0;

    for iz = 1:z_points
        delta_z         = z_vec(iz) - beam.z_focus;
        w_z             = beam.w0 * sqrt(1 + (delta_z / beam.zR)^2);
        I_row           = (beam.w_surface / w_z)^2 * exp(-2 * (y_vec - beam_y_center).^2 / w_z^2);
        I_map(iz, :)    = I_surface_peak * I_row * exp(-accumulated_att);
        acc_att_vec(iz) = accumulated_att;

        if iz < z_points
            I_cur    = I_map(iz, :);
            avg_mu_t = sum(mu_t_map(iz,:) .* I_cur) / sum(I_cur);
            accumulated_att = accumulated_att + avg_mu_t * dz;
        end
    end
end
