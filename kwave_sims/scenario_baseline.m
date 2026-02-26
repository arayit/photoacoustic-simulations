clear all; close all; clc;

% =========================================================================
% Scenario: baseline — single absorbing target, no nonlinear excitation
% =========================================================================

% --- Beam ---
cfg.lambda         = 1064e-9;       % wavelength [m]
cfg.NA             = 0.55;          % numerical aperture (Mitutoyo Plan Apo)
cfg.n              = 1.33;          % refractive index (water/tissue)
cfg.target_depth   = 3e-3;          % focal depth [m]
cfg.target_radius  = 5e-6;          % target radius [m]

% --- Input radiation ---
cfg.fluence_focus  = 20;            % peak fluence at focus [J/cm^2]
cfg.pulse_duration = 5e-9;          % pulse duration [s]

% --- Gruneisen ---
cfg.Gamma          = 0.12;

% --- Tissue optical properties @ 1064 nm [m^-1] ---
cfg.mu_a_tissue    = 18;
cfg.mu_s_tissue    = 91;

% --- Target optical properties [m^-1] ---
cfg.mu_a_target    = 500;
cfg.mu_s_target    = 10;
cfg.alpha2_target  = 9e-13;         % TPA [m/W]
cfg.alpha3_target  = 0;             % 3PA [m^2/W^2]

% --- Acoustic medium ---
cfg.c_sound        = 1500;          % [m/s]
cfg.rho            = 1000;          % [kg/m^3]
cfg.alpha_coeff    = 0.75;          % [dB/MHz^y/cm]
cfg.alpha_power    = 1.5;

% --- Transducer / detection ---
cfg.f_transducer   = 50e6;          % [Hz]
cfg.PPW_acoustic   = 10;
cfg.n_elements     = 128;

% --- Grid extents ---
cfg.z_max          = 4e-3;          % [m]
cfg.y_max          = 1.5e-3;        % [m] (half-width, grid spans ±y_max)

% --- Optical resolution ---
cfg.PPW_optical    = 5;
cfg.opt_margin     = 5;             % optical grid half-extent in target radii

cfg.verbose        = true;

% =========================================================================
% Run / load
% =========================================================================
save_path    = 'results_baseline.mat';
force_rerun  = false;

if ~force_rerun && exist(save_path, 'file')
    fprintf('Loading existing results from %s\n', save_path);
    load(save_path, 'results');
else
    results = run_baseline_pa(cfg);
    save(save_path, 'results', '-v7.3');
    fprintf('Results saved to %s\n', save_path);
end

% =========================================================================
% Visualize
% =========================================================================
visualize_pa(results);
