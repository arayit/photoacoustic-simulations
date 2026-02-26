clear all; close all; clc;

show_plots = true;

% --- Parameters ---
lambda         = 1064e-9;
NA             = 0.55;
n              = 1.33;
target_depth   = 3e-3;

fluence        = 20;        % surface fluence [J/cm^2]
pulse_duration = 5e-9;      % pulse duration [s]

z_max = 4e-3;
y_max = 1.5e-3;
dz    = 2e-6;
dy    = 1e-6;

% --- Grid ---
z_points = round(z_max / dz);
y_points = round(2*y_max / dy);
dz = z_max / z_points;
dy = 2*y_max / y_points;
z_vec = linspace(0, z_max, z_points);
y_vec = linspace(-y_max, y_max, y_points);

% --- Beam ---
I_surface_peak = (fluence * 1e4) / pulse_duration;   % [W/m^2]

beam  = gaussian_beam_params(lambda, NA, n, target_depth);
I_map = build_intensity_map(beam, z_vec, y_vec, I_surface_peak);

fprintf('w0      = %.3f um\n', beam.w0*1e6);
fprintf('zR      = %.3f um\n', beam.zR*1e6);
fprintf('w_surf  = %.2f um\n', beam.w_surface*1e6);
fprintf('focus   = %.0f um\n', beam.z_focus*1e6);

if show_plots
    figure;
    imagesc(y_vec*1e6, z_vec*1e6, I_map);
    axis image; colormap hot; colorbar;
    xlabel('y [um]'); ylabel('z [um]');
    title('Intensity map [W/m^2]');
    hold on;
    plot(xlim, [beam.z_focus*1e6, beam.z_focus*1e6], 'w--', 'LineWidth', 1);
    hold off;
end
