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
base.alpha2_target = 9e-13;         % [m/W]
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
% Scenario 1: NS single pulse, tau = 10 ns, F = 10 J/cm^2
% =========================================================================
cfg            = base;
cfg.label      = 's01_ns_tau10ns_F10';
cfg.pulse_duration = 10e-9;         % [s]
cfg.fluence_focus  = 10;            % [J/cm^2]

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
% Add further scenarios below following the same pattern
% =========================================================================
