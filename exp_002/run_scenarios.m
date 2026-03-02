clearvars; close all; clc;

% =========================================================================
% exp_002 — Run all scenarios and save results
%
% Identical to exp_001 with all fluence values 10× stronger:
%   s01: F  = 10 J/cm²   (was 1)
%   s02: Fp = 1  J/cm²   (was 0.1)
%   s03: Fp = 1  J/cm²   (was 0.1)
%
% Common parameters:
%   lambda       = 1064 nm
%   NA           = 0.55
%   target_depth = 3 mm
%   contrast agent: BODIPY-TR (alpha1=0, alpha2=9e-14 m/W, alpha3=0)
%
% Assumed (not scenario-specific, held constant):
%   target_radius = 5 um
%   n             = 1.33  (water/tissue)
%   Gamma         = 0.12
%   mu_a_tissue   = 18  m^-1  @ 1064 nm
%   mu_s_tissue   = 91  m^-1  @ 1064 nm
%   mu_s_target   = 0         (dye in solution — negligible scattering)
%   c_sound       = 1500 m/s
%   rho           = 1000 kg/m^3
%   alpha_coeff   = 0.75 dB/MHz^y/cm
%   alpha_power   = 1.5
%   f_transducer  = 50 MHz
%   PPW_acoustic  = 10
%   n_elements    = 128
%   z_max         = 6 mm
%   y_max         = 1.5 mm
%   PPW_optical   = 5
%   opt_margin    = 5
%   pml_size      = 40
% =========================================================================

% --- Paths ---
study_dir   = fileparts(mfilename('fullpath'));
addpath(fullfile(study_dir, '..', 'engine'));
results_dir = fullfile(study_dir, 'results');

force_rerun = false;

% --- Progress tracking ---
N_list    = 10:10:300;
n_total   = 2 + numel(N_list);     % s01 + s02 + 30 burst = 32
sidx      = 0;                      % scenario counter
t_runs    = [];                     % elapsed time per completed run (for ETA)
t_start   = tic;                    % wall clock for total elapsed

% =========================================================================
% Base cfg — shared across all scenarios
% =========================================================================
base.lambda        = 1064e-9;       % [m]
base.NA            = 0.55;
base.n             = 1.33;
base.target_depth  = 3e-3;          % [m]
base.target_radius = 5e-6;          % [m]
base.Gamma         = 0.12;

base.mu_a_tissue   = 18;            % [m^-1]
base.mu_s_tissue   = 91;            % [m^-1]

% BODIPY-TR: no linear absorption, TPA only
base.mu_a_target   = 0;             % alpha1 = 0
base.mu_s_target   = 0;             % dye solution — no scattering
base.alpha2_target = 9e-14;         % [m/W] — ~280 GM at 1 mM
base.alpha3_target = 0;

base.c_sound       = 1500;          % [m/s]
base.rho           = 1000;          % [kg/m^3]
base.alpha_coeff   = 0.75;          % [dB/MHz^y/cm]
base.alpha_power   = 1.5;

base.f_transducer  = 50e6;          % [Hz]
base.PPW_acoustic  = 10;
base.n_elements    = 128;

base.z_max         = 6e-3;          % [m]
base.y_max         = 1.5e-3;        % [m]
base.PPW_optical   = 5;
base.opt_margin    = 5;
base.pml_size      = 40;
base.verbose       = false;         % suppress engine output — progress shown here

fprintf('=== exp_002 | %d scenarios | %s ===\n\n', n_total, datestr(now, 'yyyy-mm-dd HH:MM:SS'));

% =========================================================================
% Scenario 1: NS single pulse, tau = 3 ns, F = 10 J/cm^2
% =========================================================================
sidx      = sidx + 1;
cfg       = base;
cfg.label = 's01_ns_tau3ns_F10';
cfg.pulse_duration = 3e-9;          % [s]
cfg.fluence_focus  = 10;            % [J/cm^2]  — 10x exp_001

save_path = fullfile(results_dir, [cfg.label '.mat']);
fprintf('[%02d/%02d] %s ', sidx, n_total, cfg.label);
t0 = tic;
if ~force_rerun && exist(save_path, 'file')
    fprintf('— loaded\n');
else
    fprintf('— running...\n');
    results = run_pa_sim(cfg);
    save(save_path, 'results', '-v7.3');
    t_runs(end+1) = toc(t0);
    fprintf('        done in %s\n', format_duration(t_runs(end)));
end
print_progress(sidx, n_total, t_start, t_runs);

% =========================================================================
% Scenario 2: FS single pulse, taup = 100 fs, Fp = 1 J/cm^2
% =========================================================================
sidx      = sidx + 1;
cfg       = base;
cfg.label = 's02_fs_tau100fs_F1';
cfg.pulse_duration = 100e-15;       % [s]
cfg.fluence_focus  = 1;             % [J/cm^2]  — 10x exp_001

save_path = fullfile(results_dir, [cfg.label '.mat']);
fprintf('[%02d/%02d] %s ', sidx, n_total, cfg.label);
t0 = tic;
if ~force_rerun && exist(save_path, 'file')
    fprintf('— loaded\n');
else
    fprintf('— running...\n');
    results = run_pa_sim(cfg);
    save(save_path, 'results', '-v7.3');
    t_runs(end+1) = toc(t0);
    fprintf('        done in %s\n', format_duration(t_runs(end)));
end
print_progress(sidx, n_total, t_start, t_runs);

% =========================================================================
% Scenario 3: FS burst mode, taup = 100 fs, Fp = 1 J/cm^2 per pulse
%             tau_burst = 3 ns, N = 10:10:300
% =========================================================================
taup      = 100e-15;    % fs pulse duration [s]
Fp        = 1;          % fluence per pulse [J/cm^2]  — 10x exp_001
tau_burst = 3e-9;       % burst window [s] — metadata only

for N = N_list
    sidx      = sidx + 1;
    cfg       = base;
    cfg.label = sprintf('s03_burst_N%03d', N);
    cfg.pulse_duration  = taup * N;
    cfg.fluence_focus   = Fp * N;
    cfg.burst_N         = N;
    cfg.burst_taup      = taup;
    cfg.burst_Fp        = Fp;
    cfg.burst_tau       = tau_burst;

    save_path = fullfile(results_dir, [cfg.label '.mat']);
    fprintf('[%02d/%02d] %s ', sidx, n_total, cfg.label);
    t0 = tic;
    if ~force_rerun && exist(save_path, 'file')
        fprintf('— loaded\n');
    else
        fprintf('— running...\n');
        results = run_pa_sim(cfg);
        save(save_path, 'results', '-v7.3');
        t_runs(end+1) = toc(t0);
        fprintf('        done in %s\n', format_duration(t_runs(end)));
    end
    print_progress(sidx, n_total, t_start, t_runs);
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
