clearvars; close all; clc;

% =========================================================================
% exp_003 — Results visualization
%
% Assembles B-scan images from the OR-PAM scan and produces:
%   Figure 1 — B-scan for each illumination scenario (3 panels)
%   Figure 2 — Lateral profile (max projection along depth) for all 3
% =========================================================================

study_dir   = fileparts(mfilename('fullpath'));
results_dir = fullfile(study_dir, 'results');

% --- Scan parameters (must match run_scenarios.m) ---
y_scan_list = (-65:2:65) * 1e-6;       % [m]
n_scan      = numel(y_scan_list);
c_sound     = 1500;                     % [m/s]

N_burst    = 300;
scen_info  = { ...
    's01_ns',                 'NS  (3 ns, 13.2 J/cm^2)'; ...
    's02_fs',                 'FS  (100 fs, 1 J/cm^2)'; ...
    sprintf('s03_b%03d', N_burst), sprintf('FS burst N=%d  (100 fs, 1 J/cm^2/pulse)', N_burst)};
n_scen = size(scen_info, 1);

% =========================================================================
% Load results and assemble B-scans
% =========================================================================
bscans  = cell(n_scen, 1);
t_array = [];
elem_y  = [];

for is = 1:n_scen
    prefix = scen_info{is, 1};
    bs     = [];

    for k = 1:n_scan
        y_scan = y_scan_list(k);
        y_um   = round(y_scan * 1e6);
        if y_um >= 0
            y_str = sprintf('p%03d', y_um);
        else
            y_str = sprintf('n%03d', abs(y_um));
        end

        fname = fullfile(results_dir, [prefix '_y_' y_str '.mat']);
        if ~exist(fname, 'file')
            error('Missing: %s\nRun run_scenarios.m first.', fname);
        end
        r = load(fname, 'results');

        if isempty(t_array)
            t_array = double(r.results.t_array);
            elem_y  = r.results.element_y;
        end

        % element closest to beam position (co-aligned detector)
        [~, i_elem] = min(abs(elem_y - y_scan));
        a_scan      = double(r.results.sensor_data(i_elem, :));
        bs(:, k)    = abs(hilbert(a_scan));
    end

    bscans{is} = bs;
end

z_axis    = c_sound * t_array / 2 * 1e3;   % depth [mm]
y_axis_um = y_scan_list * 1e6;              % lateral [um]
z_target  = 3;                              % target depth [mm]

% =========================================================================
% Figure 1 — B-scan panels
% =========================================================================
fig1 = figure('Color', 'w', 'Position', [50 50 1200 380]);
clim_db = [-40 0];

for is = 1:n_scen
    ax    = subplot(1, n_scen, is);
    bs_db = 20 * log10(bscans{is} / max(bscans{is}(:)) + eps);

    imagesc(ax, y_axis_um, z_axis, bs_db, clim_db);
    colormap(ax, 'hot');
    axis(ax, 'tight');
    set(ax, 'YDir', 'reverse');

    xlabel(ax, 'Lateral position (\mum)');
    if is == 1, ylabel(ax, 'Depth z (mm)'); end
    title(ax, scen_info{is, 2});

    hold(ax, 'on');
    xline(ax, 0,        'c--', 'LineWidth', 1);   % target centre
    yline(ax, z_target, 'c--', 'LineWidth', 1);   % target depth
    hold(ax, 'off');
end

cb = colorbar('eastoutside');
ylabel(cb, 'Amplitude (dB)');
sgtitle('exp\_003 — OR-PAM B-scan (single target)', 'FontSize', 13);
exportgraphics(fig1, fullfile(study_dir, 'bscan_comparison.png'), 'Resolution', 300);
fprintf('Figure 1 saved: bscan_comparison.png\n');

% =========================================================================
% Figure 2 — Lateral profile
% =========================================================================
fig2   = figure('Color', 'w', 'Position', [50 480 800 380]);
colors = {'r', 'k', 'b'};
hold on;

for is = 1:n_scen
    lat_prof = max(bscans{is}, [], 1);
    lat_prof = lat_prof / max(lat_prof);
    plot(y_axis_um, lat_prof, [colors{is} '-o'], ...
        'LineWidth', 1.5, 'MarkerSize', 3, ...
        'DisplayName', scen_info{is, 2});
end

xline(0, 'k:', 'LineWidth', 1, 'HandleVisibility', 'off');
xlabel('Lateral position (\mum)');
ylabel('Normalised peak PA amplitude');
title('exp\_003 — Lateral Profile (max projection along depth)');
legend('Location', 'north');
grid on; box on;

exportgraphics(fig2, fullfile(study_dir, 'lateral_profile.png'), 'Resolution', 300);
fprintf('Figure 2 saved: lateral_profile.png\n');
