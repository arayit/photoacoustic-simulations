clearvars; close all; clc;

% =========================================================================
% exp_009 — TPA-PAM feasibility limits (ballistic regime)
%
% Ballistic-photon model with corrected full scattering coefficient.
% Tissue: native porcine liver @ 1070 nm (Ritz et al.)
%   mu_a = 18 m^-1,  mu_s = 4340 m^-1 (full, NOT reduced)
%
% Sweep axes:
%   depth   (7): 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0 mm
%   pulse   (7): NS, FS, burst N = 10, 50, 100, 500, 1000
%   alpha2  (3): 9e-14, 9e-13, 9e-12 m/W
%
% Total: 7 x 7 x 3 = 147 scenarios
% =========================================================================

% --- Paths ---
study_dir   = fileparts(mfilename('fullpath'));
addpath(fullfile(study_dir, '..', '..', 'engine'));
results_dir = fullfile(study_dir, 'results');
if ~exist(results_dir, 'dir'), mkdir(results_dir); end

force_rerun = true;

% --- Sweep grids ---
depth_list  = [0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0] * 1e-3;   % [m]
alpha2_list = [9e-14, 9e-13, 9e-12];                             % [m/W]
alpha2_tags = {'a1', 'a2', 'a3'};   % labels for filenames

% --- Pulse types ---
pulse_types = struct();

pulse_types(1).tag            = 'ns';
pulse_types(1).pulse_duration = 1e-9;
pulse_types(1).fluence_focus  = 1.0;
pulse_types(1).burst_N        = 1;

pulse_types(2).tag            = 'fs';
pulse_types(2).pulse_duration = 100e-15;
pulse_types(2).fluence_focus  = 0.1;
pulse_types(2).burst_N        = 1;

burst_N_list = [10, 50, 100, 500, 1000];
for k = 1:numel(burst_N_list)
    idx = 2 + k;
    pulse_types(idx).tag            = sprintf('b%04d', burst_N_list(k));
    pulse_types(idx).pulse_duration = 100e-15;
    pulse_types(idx).fluence_focus  = 0.1;
    pulse_types(idx).burst_N        = burst_N_list(k);
end

n_total = numel(alpha2_list) * numel(pulse_types) * numel(depth_list);
sidx    = 0;
t_runs  = [];
t_start = tic;

% =========================================================================
% Base cfg
% =========================================================================
base.lambda        = 1064e-9;
base.NA            = 0.50;
base.n             = 1.33;
base.target_radius = 5e-6;
base.Gamma         = 0.12;

% Optical properties: native porcine liver @ 1070 nm (Ritz et al.)
% mu_s is the FULL scattering coefficient (ballistic-photon model).
base.mu_a_tissue   = 18;              % [m^-1]  (0.018 mm^-1)
base.mu_s_tissue   = 4340;            % [m^-1]  (4.34 mm^-1)

base.mu_a_target   = 0;
base.mu_s_target   = 0;
base.alpha3_target = 0;

base.c_sound       = 1500;
base.rho           = 1000;
base.alpha_coeff   = 0.75;
base.alpha_power   = 1.5;

base.f_grid        = 50e6;            % [Hz] — sets dx ~ 3 um
base.PPW_acoustic  = 10;
base.n_elements    = 128;

base.y_max         = 1.5e-3;
base.PPW_optical   = 5;
base.opt_margin    = 5;
base.pml_size      = 40;

base.snr_dB        = 40;
base.verbose       = false;

tau_burst = 1e-9;   % burst window [s]

fprintf('=== exp_009 feasibility limits | %d scenarios | %s ===\n\n', ...
        n_total, datestr(now, 'yyyy-mm-dd HH:MM:SS'));

% =========================================================================
% Main loop: alpha2 x pulse type x depth
% =========================================================================
for ai = 1:numel(alpha2_list)
    for pt = pulse_types
        for depth = depth_list
            sidx      = sidx + 1;
            cfg       = base;
            depth_um  = round(depth * 1e6);

            cfg.alpha2_target = alpha2_list(ai);
            cfg.label         = sprintf('%s_%s_d%04dum', ...
                                        alpha2_tags{ai}, pt.tag, depth_um);
            cfg.target_depth  = depth;
            cfg.z_max         = depth + 2e-3;
            cfg.pulse_duration = pt.pulse_duration;
            cfg.fluence_focus  = pt.fluence_focus;

            if pt.burst_N > 1
                cfg.burst_N   = pt.burst_N;
                cfg.burst_tau = tau_burst;
            end

            save_path = fullfile(results_dir, [cfg.label '.mat']);
            fprintf('[%03d/%03d] %s ', sidx, n_total, cfg.label);
            t0 = tic;
            if ~force_rerun && exist(save_path, 'file')
                fprintf('-- loaded\n');
            else
                fprintf('-- running...\n');
                results = run_pa_sim(cfg);
                save(save_path, 'results', '-v7.3');
                t_runs(end+1) = toc(t0);
                fprintf('          done in %s\n', format_duration(t_runs(end)));
            end
            print_progress(sidx, n_total, t_start, t_runs);
        end
    end
end

fprintf('\n=== All done | Total time: %s ===\n', format_duration(toc(t_start)));

% =========================================================================
% Local functions
% =========================================================================
function print_progress(sidx, n_total, t_start, t_runs)
    elapsed = toc(t_start);
    if isempty(t_runs)
        fprintf('          elapsed: %s\n\n', format_duration(elapsed));
        return;
    end
    remaining = n_total - sidx;
    eta       = mean(t_runs) * remaining;
    fprintf('          elapsed: %s | ETA: ~%s (%d remaining)\n\n', ...
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
