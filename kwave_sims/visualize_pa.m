function visualize_pa(results)
% VISUALIZE_PA  Visualize photoacoustic simulation results.
%
%   visualize_pa(results)        — pass results struct from run_pa_sim
%   visualize_pa('results_baseline.mat')  — load from file and visualize
%
%   Panels:
%     1. Initial pressure p0 on optical grid
%     2. B-scan (sensor_data: all elements vs time/depth)
%     3. Central element RF trace

if ischar(results) || isstring(results)
    s = load(results, 'results');
    results = s.results;
end

sensor_data  = results.sensor_data;
kgrid        = results.kgrid;
element_y    = results.element_y;
p0_opt       = results.p0_opt;
z_opt_vec    = results.z_opt_vec;
y_opt_vec    = results.y_opt_vec;
cfg          = results.cfg;

c_sound      = cfg.c_sound;
target_depth = cfg.target_depth;

% --- Time / depth axis ---
t_vec      = kgrid.t_array;             % [1 x Nt]
depth_vec  = t_vec * c_sound * 1e3;    % one-way depth [mm]

% --- Ensure sensor_data is [n_elements x Nt] ---
Nt = kgrid.Nt;
if size(sensor_data, 1) == Nt
    sensor_data = sensor_data';
end
n_el      = size(sensor_data, 1);
center_el = round(n_el / 2);

% -------------------------------------------------------------------------
if isfield(cfg, 'label')
    fig_title = ['Photoacoustic Simulation — ' cfg.label];
else
    fig_title = 'Photoacoustic Simulation';
end

figure('Color', 'k', 'Position', [80 80 1400 480]);
tl = tiledlayout(1, 3, 'TileSpacing', 'compact', 'Padding', 'compact');
title(tl, fig_title, 'Color', 'w', 'FontSize', 13);

% --- Panel 1: p0 on optical grid ---
ax1 = nexttile;
imagesc(y_opt_vec * 1e6, z_opt_vec * 1e6, p0_opt);
axis image;
colormap(ax1, hot);
cb1 = colorbar; cb1.Color = 'w';
ylabel(cb1, 'p_0 (Pa)');
xlabel('y (µm)'); ylabel('z (µm)');
title('Initial pressure p_0');
set(ax1, 'Color', 'k', 'XColor', 'w', 'YColor', 'w', 'YDir', 'normal');
ax1.Title.Color = 'w';

% --- Panel 2: B-scan ---
ax2 = nexttile;
imagesc(depth_vec, element_y * 1e3, sensor_data);
colormap(ax2, gray);
cb2 = colorbar; cb2.Color = 'w';
ylabel(cb2, 'Pressure (Pa)');
xlabel('Depth (mm)'); ylabel('Element position (mm)');
title('B-scan (raw PA)');
xline(target_depth * 1e3, 'r--', 'LineWidth', 1.2);
set(ax2, 'Color', 'k', 'XColor', 'w', 'YColor', 'w');
ax2.Title.Color = 'w';

% --- Panel 3: Central element RF trace ---
ax3 = nexttile;
plot(depth_vec, sensor_data(center_el, :), 'w', 'LineWidth', 1);
hold on;
xline(target_depth * 1e3, 'r--', sprintf('%.1f mm', target_depth*1e3), ...
    'LabelColor', 'r', 'Color', 'r', 'LineWidth', 1.2);
xlabel('Depth (mm)'); ylabel('Pressure (Pa)');
title(sprintf('Element %d (center)', center_el));
set(ax3, 'Color', 'k', 'XColor', 'w', 'YColor', 'w');
ax3.Title.Color = 'w';
ax3.XAxis.Limits = [0, max(depth_vec)];
