clearvars; close all; clc;

% =========================================================================
% exp_001 — Run all scenarios and save results
%
% Common parameters:
%   lambda       = 1064 nm
%   NA           = 0.55
%   target_depth = 3 mm
%   contrast agent: BODIPY-TR (alpha1=0, alpha2=9e-13 m/W, alpha3=0)
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
study_dir = fileparts(mfilename('fullpath'));
addpath(fullfile(study_dir, '..', 'engine'));
results_dir = fullfile(study_dir, 'results');

force_rerun = false;

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
base.verbose       = true;

% =========================================================================
% Scenario 1: NS single pulse, tau = 3 ns, F = 10 J/cm^2
% tau = 3 ns chosen to satisfy stress confinement (tau_stress ~ r/c ~ 3.3 ns)
% =========================================================================
cfg            = base;
cfg.label      = 's01_ns_tau3ns_F1';
cfg.pulse_duration = 3e-9;          % [s]
cfg.fluence_focus  = 1;             % [J/cm^2]

save_path = fullfile(results_dir, [cfg.label '.mat']);
if ~force_rerun && exist(save_path, 'file')
    fprintf('[s01] Loading existing results.\n');
else
    fprintf('[s01] Running...\n');
    results = run_pa_sim(cfg);
    save(save_path, 'results', '-v7.3');
    fprintf('[s01] Saved: %s\n', save_path);
end

% =========================================================================
% Scenario 2: FS single pulse, taup = 100 fs, Fp = 1 J/cm^2
% =========================================================================
cfg                = base;
cfg.label          = 's02_fs_tau100fs_F01';
cfg.pulse_duration = 100e-15;       % [s]
cfg.fluence_focus  = 0.1;           % [J/cm^2]

save_path = fullfile(results_dir, [cfg.label '.mat']);
if ~force_rerun && exist(save_path, 'file')
    fprintf('[s02] Loading existing results.\n');
else
    fprintf('[s02] Running...\n');
    results = run_pa_sim(cfg);
    save(save_path, 'results', '-v7.3');
    fprintf('[s02] Saved: %s\n', save_path);
end

% =========================================================================
% Scenario 3: FS burst mode, taup = 100 fs, Fp = 1 J/cm^2 per pulse
%             tau_burst = 3 ns, N = 50:50:500
%
% tau_burst = 3 ns chosen to satisfy stress confinement (tau_stress ~ 3.3 ns).
%
% Model: burst of N identical fs pulses, energy superposition assumed.
%   I_peak = Fp / taup  (peak intensity per pulse)
%   Q      = (mu_a*I_peak + alpha2*I_peak^2) * taup * N
%
% Mapped onto engine by:
%   fluence_focus  = Fp * N   (total fluence over burst)
%   pulse_duration = taup * N (effective duration — preserves I_peak)
%
% With tau_burst within stress confinement, energy superposition is a
% valid approximation — no need to simulate each pulse individually.
% =========================================================================
taup      = 100e-15;    % fs pulse duration [s]
Fp        = 0.1;        % fluence per pulse [J/cm^2]
tau_burst = 3e-9;       % burst window [s] — recorded as metadata only
N_list    = 10:10:300;

for N = N_list
    cfg                = base;
    cfg.label          = sprintf('s03_burst_N%03d', N);
    cfg.pulse_duration = taup * N;  % effective duration [s]
    cfg.fluence_focus  = Fp * N;    % total fluence [J/cm^2]

    % Burst metadata (stored in cfg for reference, not used by engine)
    cfg.burst_N        = N;
    cfg.burst_taup     = taup;
    cfg.burst_Fp       = Fp;
    cfg.burst_tau_burst = tau_burst;

    save_path = fullfile(results_dir, [cfg.label '.mat']);
    if ~force_rerun && exist(save_path, 'file')
        fprintf('[s03 N=%d] Loading existing results.\n', N);
    else
        fprintf('[s03 N=%d] Running...\n', N);
        results = run_pa_sim(cfg);
        save(save_path, 'results', '-v7.3');
        fprintf('[s03 N=%d] Saved: %s\n', N, save_path);
    end
end
