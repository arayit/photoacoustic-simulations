clearvars; close all; clc;

% =========================================================================
% exp_008 — Burst repetition rate comparison: 100 GHz vs 1 THz
%
% Based on exp_007 but with corrected ballistic-photon scattering:
%   mu_s = 4340 m^-1 (full scattering coeff, native porcine liver,
%                      Ritz et al., 1070 nm)
% Fixed burst window tau_burst = 1 ns.
%   N=100  -> f_R = 100 GHz  (same as exp_007)
%   N=1000 -> f_R = 1000 GHz (1 THz)
%
% Pulse types (2):
%   b0100 : burst N=100,  tau=100 fs, F=0.1 J/cm^2/pulse, tau_burst=1 ns
%   b1000 : burst N=1000, tau=100 fs, F=0.1 J/cm^2/pulse, tau_burst=1 ns
%
% Depths (7): 0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0 mm
% Total: 2 x 7 = 14 scenarios
% =========================================================================

% --- Paths ---
study_dir   = fileparts(mfilename('fullpath'));
addpath(fullfile(study_dir, '..', '..', 'engine'));
results_dir = fullfile(study_dir, 'results');
if ~exist(results_dir, 'dir'), mkdir(results_dir); end

force_rerun = true;

% --- Depth sweep ---
depth_list = [0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0] * 1e-3;   % [m]  7 depths

% --- Pulse types ---
pulse_types = struct();
pulse_types(1).tag            = 'b0100';
pulse_types(1).pulse_duration = 100e-15;
pulse_types(1).fluence_focus  = 0.1;
pulse_types(1).burst_N        = 100;

pulse_types(2).tag            = 'b1000';
pulse_types(2).pulse_duration = 100e-15;
pulse_types(2).fluence_focus  = 0.1;
pulse_types(2).burst_N        = 1000;

n_total = numel(pulse_types) * numel(depth_list);
sidx    = 0;
t_runs  = [];
t_start = tic;

% =========================================================================
% Base cfg (identical to exp_007)
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
base.alpha2_target = 9e-14;           % [m/W] — ~28 GM at 1 mM
base.alpha3_target = 0;

base.c_sound       = 1500;
base.rho           = 1000;
base.alpha_coeff   = 0.75;
base.alpha_power   = 1.5;

base.f_grid        = 50e6;            % [Hz] — sets dx = 3 um
base.PPW_acoustic  = 10;
base.n_elements    = 128;

base.y_max         = 1.5e-3;
base.PPW_optical   = 5;
base.opt_margin    = 5;
base.pml_size      = 40;

base.snr_dB        = 40;
base.verbose       = false;

tau_burst = 1e-9;   % burst window [s] — fixed for both

fprintf('=== exp_008 burst rate comparison | %d scenarios | %s ===\n\n', ...
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
        cfg.z_max         = depth + 2e-3;
        cfg.pulse_duration = pt.pulse_duration;
        cfg.fluence_focus  = pt.fluence_focus;
        cfg.burst_N   = pt.burst_N;
        cfg.burst_tau = tau_burst;

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
