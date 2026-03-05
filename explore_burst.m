clearvars; close all; clc;

% Add engine to path
addpath(fullfile(fileparts(mfilename('fullpath')), 'engine'));

% =========================================================================
% Burst parameters — edit these
% =========================================================================
N         = 100;       % number of fs pulses in burst
Fp        = 1;         % fluence per pulse [J/cm^2]
taup      = 100e-15;   % single-pulse duration [s]
tau_burst = 3e-9;      % burst window duration [s]  (fixed; f_r = N/tau_burst varies)

f_r = N / tau_burst;   % intra-burst repetition rate [Hz]  — derived, not free

% =========================================================================
% cfg
% =========================================================================
cfg.label = sprintf('burst_N%03d_Fp%.3g_taup%.0ffs', N, Fp, taup * 1e15);

% Beam
cfg.lambda        = 1064e-9;       % wavelength [m]
cfg.NA            = 0.55;
cfg.n             = 1.33;
cfg.target_depth  = 3e-3;          % [m]
cfg.target_radius = 5e-6;          % [m]

% Burst metadata
cfg.burst_N         = N;
cfg.burst_Fp        = Fp;
cfg.burst_taup      = taup;
cfg.burst_tau       = tau_burst;
cfg.burst_f_r       = f_r;

% Burst-to-engine mapping
cfg.fluence_focus  = Fp * N;       % total burst fluence [J/cm^2]
cfg.pulse_duration = tau_burst;    % burst window [s] — f_r = N/tau_burst varies with N

% Gruneisen
cfg.Gamma         = 0.12;

% Tissue optical properties @ 1064 nm [m^-1]
cfg.mu_a_tissue   = 18;
cfg.mu_s_tissue   = 91;

% Target: BODIPY-TR — TPA only, no linear absorption
cfg.mu_a_target   = 0;
cfg.mu_s_target   = 0;
cfg.alpha2_target = 9e-14;         % TPA [m/W]
cfg.alpha3_target = 0;

% Acoustic medium
cfg.c_sound       = 1500;          % [m/s]
cfg.rho           = 1000;          % [kg/m^3]
cfg.alpha_coeff   = 0.75;
cfg.alpha_power   = 1.5;

% Grid / detection
cfg.f_grid  = 50e6;          % [Hz]
cfg.PPW_acoustic  = 10;
cfg.n_elements    = 128;

% Grid
cfg.z_max         = 6e-3;          % [m]
cfg.y_max         = 1.5e-3;        % [m]

% Solver
cfg.PPW_optical   = 5;
cfg.opt_margin    = 5;
cfg.pml_size      = 40;
cfg.verbose       = true;

% =========================================================================
% Run and visualize
% =========================================================================
results = run_pa_sim(cfg);
visualize_pa(results);
