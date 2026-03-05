clearvars; close all; clc;

% =========================================================================
% exp_004 — Run all scenarios and save results
%
% Identical to exp_002 with BODIPY-TR concentration 10x higher:
%   alpha2_target = 9e-13 m/W   (~280 GM at 10 mM)
%
% Three scenarios:
%   s01: NS single pulse,  tau  = 3 ns,   F  = 10 J/cm²
%   s02: FS single pulse,  taup = 100 fs, Fp = 1  J/cm²
%   s03: FS burst mode,    taup = 100 fs, Fp = 1  J/cm²  per pulse,
%        tau_burst = 3 ns, N = 10:10:300
%
% NOTE on burst mode encoding (s03)
%   pulse_duration = taup  (single-pulse duration)
%   fluence_focus  = Fp    (per-pulse fluence)
%   burst_N        = N
%   Engine: Q = burst_N * alpha2 * I^2 * pulse_duration
%   This gives Q proportional to N (linear), which is correct physics.
%
% Contrast agent: BODIPY-TR at 10 mM
%   mu_a_target   = 0       (no linear absorption at 1064 nm)
%   alpha2_target = 9e-13   [m/W]  ~280 GM at 10 mM
%   alpha3_target = 0
%
% Noise model:
%   snr_dB = 40   [dB, peak-referenced Gaussian noise via k-Wave addNoise]
%
% Common parameters (held constant across all scenarios):
%   lambda       = 1064 nm
%   NA           = 0.55
%   target_depth = 3 mm
%   target_radius= 5 um
%   n            = 1.33  (water/tissue)
%   Gamma        = 0.12
%   mu_a_tissue  = 18  m^-1  @ 1064 nm
%   mu_s_tissue  = 91  m^-1  @ 1064 nm
%   mu_s_target  = 0         (dye in solution)
%   c_sound      = 1500 m/s
%   rho          = 1000 kg/m^3
%   alpha_coeff  = 0.75 dB/MHz^y/cm
%   alpha_power  = 1.5
%   f_grid = 50 MHz
%   PPW_acoustic = 10
%   n_elements   = 128
%   z_max        = 6 mm
%   y_max        = 1.5 mm
%   PPW_optical  = 5
%   opt_margin   = 5
%   pml_size     = 40
% =========================================================================

% --- Paths ---
study_dir   = fileparts(mfilename('fullpath'));
addpath(fullfile(study_dir, '..', 'engine'));
results_dir = fullfile(study_dir, 'results');
if ~exist(results_dir, 'dir'), mkdir(results_dir); end

force_rerun = true;

% --- Progress tracking ---
N_list    = 10:10:300;
n_total   = 2 + numel(N_list);     % s01 + s02 + 30 burst = 32
sidx      = 0;
t_runs    = [];
t_start   = tic;

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

% BODIPY-TR at 10 mM: no linear absorption at 1064 nm, TPA only
base.mu_a_target   = 0;
base.mu_s_target   = 0;
base.alpha2_target = 9e-13;         % [m/W] — ~280 GM at 10 mM  (10x exp_002)
base.alpha3_target = 0;

base.c_sound       = 1500;          % [m/s]
base.rho           = 1000;          % [kg/m^3]
base.alpha_coeff   = 0.75;          % [dB/MHz^y/cm]
base.alpha_power   = 1.5;

base.f_grid  = 50e6;          % [Hz]
base.PPW_acoustic  = 10;
base.n_elements    = 128;

base.z_max         = 6e-3;          % [m]
base.y_max         = 1.5e-3;        % [m]
base.PPW_optical   = 5;
base.opt_margin    = 5;
base.pml_size      = 40;

% Noise model — 40 dB peak-referenced Gaussian noise (detector/electronic)
base.snr_dB        = 40;

base.verbose       = false;

fprintf('=== exp_004 | %d scenarios | %s ===\n\n', n_total, datestr(now, 'yyyy-mm-dd HH:MM:SS'));

% =========================================================================
% Scenario 1: NS single pulse, tau = 3 ns, F = 10 J/cm^2
% =========================================================================
sidx      = sidx + 1;
cfg       = base;
cfg.label          = 's01_ns_tau3ns_F10';
cfg.pulse_duration = 3e-9;          % [s]
cfg.fluence_focus  = 10;            % [J/cm^2]

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

% =========================================================================
% Scenario 2: FS single pulse, taup = 100 fs, Fp = 1 J/cm^2
% =========================================================================
sidx      = sidx + 1;
cfg       = base;
cfg.label          = 's02_fs_tau100fs_F1';
cfg.pulse_duration = 100e-15;       % [s]
cfg.fluence_focus  = 1;             % [J/cm^2]

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

% =========================================================================
% Scenario 3: FS burst mode, taup = 100 fs, Fp = 1 J/cm^2 per pulse
%             tau_burst = 3 ns (metadata), N = 10:10:300
%
% ENCODING: pass per-pulse values — burst_N handles the N-fold scaling.
%   I_peak = Fp / taup   (correct single-pulse intensity)
%   Q      = N * alpha2 * I_peak^2 * taup   (N * single-pulse deposition)
% =========================================================================
taup      = 100e-15;    % single fs pulse duration [s]
Fp        = 1;          % per-pulse fluence [J/cm^2]
tau_burst = 3e-9;       % burst window [s] — metadata / f_R computation only

for N = N_list
    sidx      = sidx + 1;
    cfg       = base;
    cfg.label          = sprintf('s03_burst_N%03d', N);
    cfg.pulse_duration = taup;          % single-pulse duration [s]
    cfg.fluence_focus  = Fp;            % per-pulse fluence [J/cm^2]
    cfg.burst_N        = N;
    cfg.burst_tau      = tau_burst;
    % Informational fields (not used by engine):
    cfg.burst_taup     = taup;
    cfg.burst_Fp       = Fp;

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
