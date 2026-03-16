clearvars; close all; clc;

% =========================================================================
% exp_011 — Silicon nanoparticle FCA enhancement study
%
% Tests free-carrier absorption (FCA) contribution for silicon NP contrast
% agent.  Early burst pulses generate free carriers via TPA; accumulated
% carriers increase linear absorption for subsequent pulses.
%
% Si NP optical properties at 1064 nm (Boggess et al. 1986, c-Si):
%   alpha2 (beta_TPA) = 1.5e-11 m/W  (1.5 cm/GW)
%   sigma_fc          = 5e-22  m^2   (5e-18 cm^2)
%   mu_a_target       = 1000   m^-1  (10 cm^-1, above bandgap)
%   eta_fc            = auto-derived from alpha2 / (2*hv) = 4.0e7
%
% Tissue: native grey matter @ 1100 nm (coefficients.md)
%   mu_a = 50 m^-1, mu_s = 5600 m^-1 (full, ballistic model)
%
% Pulse types (5):
%   ns    : single NS pulse, tau=1 ns,   F=1.0 J/cm^2
%   fs    : single FS pulse, tau=100 fs, F=0.1 J/cm^2
%   b0100 : burst N=100,  tau=100 fs, F=0.1 J/cm^2/pulse, tau_burst=1 ns
%   b0500 : burst N=500,  tau=100 fs, F=0.1 J/cm^2/pulse, tau_burst=1 ns
%   b1000 : burst N=1000, tau=100 fs, F=0.1 J/cm^2/pulse, tau_burst=1 ns
%
% Depths (5): 0.1, 0.2, 0.4, 0.6, 1.0 mm  (limited to 1 mm)
% Total: 5 x 5 = 25 scenarios
% =========================================================================

% --- Paths ---
study_dir   = fileparts(mfilename('fullpath'));
addpath(fullfile(study_dir, '..', '..', 'engine'));
results_dir = fullfile(study_dir, 'results');
if ~exist(results_dir, 'dir'), mkdir(results_dir); end

force_rerun = true;

% --- Depth sweep ---
depth_list = [0.1, 0.2, 0.4, 0.6, 1.0] * 1e-3;   % [m]  5 depths

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

pulse_types(3).tag            = 'b0100';
pulse_types(3).pulse_duration = 100e-15;
pulse_types(3).fluence_focus  = 0.1;
pulse_types(3).burst_N        = 100;

pulse_types(4).tag            = 'b0500';
pulse_types(4).pulse_duration = 100e-15;
pulse_types(4).fluence_focus  = 0.1;
pulse_types(4).burst_N        = 500;

pulse_types(5).tag            = 'b1000';
pulse_types(5).pulse_duration = 100e-15;
pulse_types(5).fluence_focus  = 0.1;
pulse_types(5).burst_N        = 1000;

n_total = numel(pulse_types) * numel(depth_list);
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

% Tissue: native grey matter @ 1100 nm (coefficients.md)
base.mu_a_tissue   = 50;              % [m^-1]  (0.05 mm^-1)
base.mu_s_tissue   = 5600;            % [m^-1]  (5.6 mm^-1, full scattering coeff)

% Target: silicon nanoparticle (Boggess et al. 1986, c-Si @ 1064 nm)
base.mu_a_target   = 1000;            % [m^-1]  (10 cm^-1, above-bandgap linear abs)
base.mu_s_target   = 0;
base.alpha2_target = 1.5e-11;         % [m/W]   (1.5 cm/GW, TPA)
base.alpha3_target = 0;

% FCA parameters (Boggess et al. 1986)
base.sigma_fc      = 5e-22;           % [m^2]   (5e-18 cm^2, free-carrier cross section)
% eta_fc auto-derived: alpha2 / (2*hv) = 1.5e-11 / (2*1.868e-19) ~ 4.0e7

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

fprintf('=== exp_011 Si NP FCA study | %d scenarios | %s ===\n\n', ...
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
