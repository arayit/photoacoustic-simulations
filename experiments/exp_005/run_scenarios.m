clearvars; close all; clc;

% =========================================================================
% exp_005 — Depth study: peak PA pressure vs target depth
%
% Goal: characterise how TPA-based PA signal decays with depth for
%       different illumination strategies.
%
% Pulse types (5 + NS/FS = 7):
%   ns      : NS single pulse,  tau = 3 ns,   F = 10 J/cm^2
%   fs      : FS single pulse,  tau = 100 fs, F = 1  J/cm^2
%   b040    : FS burst N = 40,  tau = 100 fs, F = 1  J/cm^2 per pulse
%   b080    : FS burst N = 80
%   b120    : FS burst N = 120
%   b160    : FS burst N = 160
%   b200    : FS burst N = 200
%
% Depths (11):  0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0 mm
%
% Total: 7 x 11 = 77 scenarios
%
% Contrast agent: BODIPY-TR at 10 mM
%   mu_a_target   = 0
%   alpha2_target = 9e-13   [m/W]  ~280 GM at 10 mM
%   alpha3_target = 0
%
% Grid: z_max = target_depth + 2 mm  (dynamic — minimises grid size)
% Noise: snr_dB = 40 dB
% =========================================================================

% --- Paths ---
study_dir   = fileparts(mfilename('fullpath'));
addpath(fullfile(study_dir, '..', '..', 'engine'));
results_dir = fullfile(study_dir, 'results');
if ~exist(results_dir, 'dir'), mkdir(results_dir); end

force_rerun = true;

% --- Depth sweep ---
depth_list = [0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0] * 1e-3;  % [m]

% --- Pulse types ---
pulse_types = struct();
pulse_types(1).tag            = 'ns';
pulse_types(1).pulse_duration = 3e-9;
pulse_types(1).fluence_focus  = 10;
pulse_types(1).burst_N        = 1;

pulse_types(2).tag            = 'fs';
pulse_types(2).pulse_duration = 100e-15;
pulse_types(2).fluence_focus  = 1;
pulse_types(2).burst_N        = 1;

for burst_N_val = [40, 80, 120, 160, 200]
    k = numel(pulse_types) + 1;
    pulse_types(k).tag            = sprintf('b%03d', burst_N_val);
    pulse_types(k).pulse_duration = 100e-15;
    pulse_types(k).fluence_focus  = 1;
    pulse_types(k).burst_N        = burst_N_val;
end

n_total = numel(pulse_types) * numel(depth_list);
sidx    = 0;
t_runs  = [];
t_start = tic;

% =========================================================================
% Base cfg
% =========================================================================
base.lambda        = 1064e-9;
base.NA            = 0.55;
base.n             = 1.33;
base.target_radius = 5e-6;
base.Gamma         = 0.12;

base.mu_a_tissue   = 18;
base.mu_s_tissue   = 91;

base.mu_a_target   = 0;
base.mu_s_target   = 0;
base.alpha2_target = 9e-13;         % [m/W] — ~280 GM at 10 mM
base.alpha3_target = 0;

base.c_sound       = 1500;
base.rho           = 1000;
base.alpha_coeff   = 0.75;
base.alpha_power   = 1.5;

base.f_grid  = 50e6;
base.PPW_acoustic  = 10;
base.n_elements    = 128;

% z_max set dynamically per scenario (target_depth + 2 mm)
base.y_max         = 1.5e-3;
base.PPW_optical   = 5;
base.opt_margin    = 5;
base.pml_size      = 40;

base.snr_dB        = 40;
base.verbose       = false;

tau_burst = 3e-9;   % burst window [s] — metadata only

fprintf('=== exp_005 depth study | %d scenarios | %s ===\n\n', ...
        n_total, datestr(now, 'yyyy-mm-dd HH:MM:SS'));

% =========================================================================
% Main loop: pulse type x depth
% =========================================================================
for pt = pulse_types
    for depth = depth_list
        sidx      = sidx + 1;
        cfg       = base;
        depth_um  = round(depth * 1e6);
        cfg.label         = sprintf('%s_d%04dum', pt.tag, depth_um);
        cfg.target_depth  = depth;
        cfg.z_max         = depth + 2e-3;   % dynamic: 2 mm clearance below target
        cfg.pulse_duration = pt.pulse_duration;
        cfg.fluence_focus  = pt.fluence_focus;

        if pt.burst_N > 1
            cfg.burst_N   = pt.burst_N;
            cfg.burst_tau = tau_burst;
        end

        save_path = fullfile(results_dir, [cfg.label '.mat']);
        fprintf('[%02d/%02d] %s ', sidx, n_total, cfg.label);
        t0 = tic;
        if ~force_rerun && exist(save_path, 'file')
            fprintf('-- loaded\n');
        else
            fprintf('-- running...\n');
            results = run_pa_sim(cfg);
            save(save_path, 'results', '-v7.3');
            t_runs(end+1) = toc(t0);
            fprintf('        done in %s\n', format_duration(t_runs(end)));
        end
        print_progress(sidx, n_total, t_start, t_runs);
    end
end

fprintf('\n=== All done | Total time: %s ===\n', format_duration(toc(t_start)));

% =========================================================================
% Local functions
% =========================================================================
function print_progress(sidx, n_total, t_start, t_runs)
    elapsed = toc(t_start);
    if isempty(t_runs)
        fprintf('        elapsed: %s\n\n', format_duration(elapsed));
        return;
    end
    remaining = n_total - sidx;
    eta       = mean(t_runs) * remaining;
    fprintf('        elapsed: %s | ETA: ~%s (%d remaining)\n\n', ...
            format_duration(elapsed), format_duration(eta), remaining);
end

function s = format_duration(sec)
    if sec < 60
        s = sprintf('%.0fs', sec);
    elseif sec < 3600
        s = sprintf('%dm %02ds', floor(sec/60), floor(mod(sec,60)));
    else
        s = sprintf('%dh %02dm', floor(sec/3600), floor(mod(sec,3600)/60));
    end
end
