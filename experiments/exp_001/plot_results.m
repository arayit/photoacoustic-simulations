clearvars; close all; clc;

% =========================================================================
% exp_001 — Results visualization
% =========================================================================

study_dir   = fileparts(mfilename('fullpath'));
results_dir = fullfile(study_dir, 'results');

% =========================================================================
% Figure 1: Peak PA signal vs burst pulse number N
% =========================================================================

% --- Reference scenarios ---
s    = load(fullfile(results_dir, 's01_ns_tau3ns_F1.mat'),    'results');
p_s01 = max(abs(s.results.sensor_data(:))) * 1e3;

s    = load(fullfile(results_dir, 's02_fs_tau100fs_F01.mat'), 'results');
p_s02 = max(abs(s.results.sensor_data(:))) * 1e3;

% --- Burst series ---
N_list  = 10:10:300;
p_burst = zeros(1, numel(N_list));

for k = 1:numel(N_list)
    N     = N_list(k);
    fname = fullfile(results_dir, sprintf('s03_burst_N%03d.mat', N));
    s     = load(fname, 'results');
    p_burst(k) = max(abs(s.results.sensor_data(:))) * 1e3;
end

% --- Plot ---
figure('Color', 'w', 'Position', [100 100 800 500]);
hold on;

plot(N_list, p_burst, 'b-o', 'LineWidth', 1.5, 'MarkerSize', 5, ...
    'DisplayName', 'FS burst  (F_p = 0.1 J/cm², \tau_p = 100 fs)');
yline(p_s01, 'r--', 'LineWidth', 1.5, ...
    'DisplayName', 'NS single pulse  (F = 1 J/cm², \tau = 3 ns)');
yline(p_s02, 'k--', 'LineWidth', 1.5, ...
    'DisplayName', 'FS single pulse  (F = 0.1 J/cm², \tau = 100 fs)');

set(gca, 'YScale', 'log');
xlabel('N (pulses per burst)');
ylabel('Peak detected pressure (mPa)');
title('exp\_001 — Peak PA Signal vs Burst Pulse Number');
legend('Location', 'northwest');
grid on; box on;
