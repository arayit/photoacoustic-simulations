function sbr = compute_sbr(results_with, results_bg)
% COMPUTE_SBR  Signal-to-background ratio from two PA simulation results.
%
%   sbr = compute_sbr(results_with, results_bg)
%
%   results_with : results struct from run_pa_sim with target present
%   results_bg   : results struct from run_pa_sim with target replaced by tissue
%
%   SBR is computed as the ratio of peak PA signal amplitudes within a time
%   window centered on the expected target arrival time.
%
%   Returns struct sbr with fields:
%     value       — linear SBR
%     dB          — 20·log10(value)
%     p_signal    — peak pressure with target [Pa]
%     p_background— peak pressure without target [Pa]
%     t_window    — [t_lo, t_hi] time window used [s]

cfg          = results_with.cfg;
c_sound      = cfg.c_sound;
target_depth = cfg.target_depth;
target_radius = cfg.target_radius;
kgrid        = results_with.kgrid;

t_vec = kgrid.t_array;
dt    = t_vec(2) - t_vec(1);

% --- Time window around target arrival ---
t_target = target_depth / c_sound;             % one-way travel time [s]
t_margin = 3 * target_radius / c_sound;        % margin based on target size
t_lo     = max(t_vec(1),   t_target - t_margin);
t_hi     = min(t_vec(end), t_target + t_margin);
it_lo    = find(t_vec >= t_lo, 1, 'first');
it_hi    = find(t_vec <= t_hi, 1, 'last');
window   = it_lo:it_hi;

% --- Ensure [n_elements x Nt] orientation ---
sd_with = results_with.sensor_data;
if size(sd_with, 1) == kgrid.Nt, sd_with = sd_with'; end

sd_bg = results_bg.sensor_data;
if size(sd_bg, 1) == kgrid.Nt, sd_bg = sd_bg'; end

% --- Peak amplitude in window ---
p_signal     = max(abs(sd_with(:, window)), [], 'all');
p_background = max(abs(sd_bg(:, window)),  [], 'all');

% --- Pack output ---
sbr.value        = p_signal / p_background;
sbr.dB           = 20 * log10(sbr.value);
sbr.p_signal     = p_signal;
sbr.p_background = p_background;
sbr.t_window     = [t_lo, t_hi];
