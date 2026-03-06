clearvars; close all; clc;

% =========================================================================
% exp_002 — Results visualization
% =========================================================================

study_dir   = fileparts(mfilename('fullpath'));
results_dir = fullfile(study_dir, 'results');

c_sound = 1500;     % [m/s]

% =========================================================================
% Load reference scenarios (used in both figures)
% =========================================================================
r_s01 = load(fullfile(results_dir, 's01_ns_tau3ns_F10.mat'),  'results');
r_s02 = load(fullfile(results_dir, 's02_fs_tau100fs_F1.mat'), 'results');

p_s01 = max(abs(r_s01.results.sensor_data(:)));
p_s02 = max(abs(r_s02.results.sensor_data(:)));

% =========================================================================
% Figure 1: Peak PA signal vs burst pulse number N
% =========================================================================
N_list  = 10:10:300;
p_burst = zeros(1, numel(N_list));

for k = 1:numel(N_list)
    N     = N_list(k);
    fname = fullfile(results_dir, sprintf('s03_burst_N%03d.mat', N));
    s     = load(fname, 'results');
    p_burst(k) = max(abs(s.results.sensor_data(:)));
end

figure('Color', 'w', 'Position', [100 100 800 500]);
hold on;

plot(N_list, p_burst, 'b-o', 'LineWidth', 1.5, 'MarkerSize', 5, ...
    'DisplayName', 'FS burst  (F_p = 1 J/cm^2, \tau_p = 100 fs)');
yline(p_s01, 'r--', 'LineWidth', 1.5, ...
    'DisplayName', sprintf('NS single pulse  (F = 10 J/cm^2, \\tau = 3 ns) — %.3g Pa', p_s01));
yline(p_s02, 'k--', 'LineWidth', 1.5, ...
    'DisplayName', sprintf('FS single pulse  (F = 1 J/cm^2, \\tau = 100 fs) — %.3g Pa', p_s02));

set(gca, 'YScale', 'log');
xlabel('N (pulses per burst)');
ylabel('Peak detected pressure (Pa)');
title('exp\_002 — Peak PA Signal vs Burst Pulse Number');
legend('Location', 'northwest');
grid on; box on;

exportgraphics(gcf, fullfile(study_dir, 'peak_pa_vs_N.png'), 'Resolution', 300);
fprintf('Figure 1 saved: peak_pa_vs_N.png\n');

% =========================================================================
% Figure 2: Characteristic PA waveforms — raw pressure, time axis
%
% Central transducer element, no normalisation.
% 3 subplots (NS / FS single / FS burst N=300) each with their own Pa
% scale so the waveform shape is visible for every scenario.
% x-axis: time [us].  Vertical line marks expected one-way arrival from
% the 3 mm target: t_arrival = target_depth / c_sound.
% =========================================================================

r_b300 = load(fullfile(results_dir, 's03_burst_N300.mat'), 'results');

% --- Shared time axis ---
t_array   = double(r_s01.results.t_array) * 1e6;   % [us]
t_arrival = 3e-3 / c_sound * 1e6;                  % expected one-way [us]

% --- Central transducer element (closest to y = 0) ---
elem_y   = r_s01.results.element_y;
[~, i_c] = min(abs(elem_y));

% --- Raw waveforms [Pa] ---
w_s01  = double(r_s01.results.sensor_data(i_c, :));
w_s02  = double(r_s02.results.sensor_data(i_c, :));
w_b300 = double(r_b300.results.sensor_data(i_c, :));

scenarios = { ...
    w_s01,  'NS  (\tau = 3 ns,   F = 10 J/cm^2)',         'r'; ...
    w_s02,  'FS  (\tau = 100 fs, F = 1 J/cm^2)',          'k'; ...
    w_b300, 'FS burst N=300  (\tau_p = 100 fs, F_p = 1 J/cm^2)', 'b'};

figure('Color', 'w', 'Position', [100 650 1000 600]);

for ip = 1:3
    ax = subplot(3, 1, ip);
    w  = scenarios{ip, 1};

    plot(ax, t_array, w, scenarios{ip, 3}, 'LineWidth', 1.5);
    xline(ax, t_arrival, 'k--', 'LineWidth', 1);
    yline(ax, 0,         'k',   'LineWidth', 0.5);

    xlabel(ax, 'Time (\mus)');
    ylabel(ax, 'Pressure (Pa)');
    title(ax, scenarios{ip, 2});
    grid(ax, 'on'); box(ax, 'on');

    % zoom to a window around the target arrival (±1 us)
    xlim(ax, [t_arrival - 1, t_arrival + 2]);
end

sgtitle('exp\_002 — PA Waveforms (central element, raw)', 'FontSize', 12);

exportgraphics(gcf, fullfile(study_dir, 'pa_waveforms.png'), 'Resolution', 300);
fprintf('Figure 2 saved: pa_waveforms.png\n');
