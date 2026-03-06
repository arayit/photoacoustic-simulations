clearvars; close all; clc;

% =========================================================================
% SBR Study — Baseline
%
% Computes signal-to-background ratio by running two simulations:
%   1. Tissue + target  (signal)
%   2. Tissue only      (background — target replaced with tissue properties)
%
% SBR = peak(signal) / peak(background)  at target depth
% =========================================================================

% --- Paths ---
study_dir  = fileparts(mfilename('fullpath'));
addpath(fullfile(study_dir, '..', 'engine'));

% =========================================================================
% Shared configuration
% =========================================================================

% --- Beam ---
cfg.lambda        = 1064e-9;        % [m]
cfg.NA            = 0.55;           % Mitutoyo Plan Apo
cfg.n             = 1.33;           % refractive index (water/tissue)
cfg.target_depth  = 3e-3;           % [m]
cfg.target_radius = 5e-6;           % [m]

% --- Input radiation ---
cfg.fluence_focus  = 20;            % [J/cm²]
cfg.pulse_duration = 100e-15;          % [s]

% --- Grüneisen ---
cfg.Gamma = 0.12;

% --- Tissue optical properties @ 1064 nm [m⁻¹] ---
cfg.mu_a_tissue = 18;
cfg.mu_s_tissue = 91;

% --- Target optical properties [m⁻¹] ---
cfg.mu_a_target   = 500;
cfg.mu_s_target   = 10;
cfg.alpha2_target = 9e-13;          % TPA [m/W]
cfg.alpha3_target = 0;              % 3PA [m²/W²]

% --- Acoustic medium ---
cfg.c_sound     = 1500;             % [m/s]
cfg.rho         = 1000;             % [kg/m³]
cfg.alpha_coeff = 0.75;             % [dB/MHz^y/cm]
cfg.alpha_power = 1.5;

% --- Grid / detection ---
cfg.f_grid = 50e6;            % [Hz]
cfg.PPW_acoustic = 10;
cfg.n_elements   = 128;

% --- Grid ---
cfg.z_max = 6e-3;                   % [m]
cfg.y_max = 1.5e-3;                 % [m]

% --- Optical resolution ---
cfg.PPW_optical = 5;
cfg.opt_margin  = 5;

% --- Solver ---
cfg.pml_size = 40;
cfg.verbose  = true;

% =========================================================================
% Run 1: tissue + target
% =========================================================================
cfg.label   = 'SBR Baseline - With Target';
save_with   = fullfile(study_dir, 'results_sbr_with_target.mat');
force_rerun = false;

if ~force_rerun && exist(save_with, 'file')
    fprintf('Loading %s\n', save_with);
    load(save_with, 'results');
    results_with = results;
else
    results_with = run_pa_sim(cfg);
    results = results_with;
    save(save_with, 'results', '-v7.3');
    fprintf('Saved: %s\n', save_with);
end

% =========================================================================
% Run 2: tissue only (background)
% =========================================================================
cfg_bg              = cfg;
cfg_bg.label        = 'SBR Baseline - Background';
cfg_bg.mu_a_target  = cfg.mu_a_tissue;  % target = tissue
cfg_bg.mu_s_target  = cfg.mu_s_tissue;
cfg_bg.alpha2_target = 0;
cfg_bg.alpha3_target = 0;

save_bg = fullfile(study_dir, 'results_sbr_background.mat');

if ~force_rerun && exist(save_bg, 'file')
    fprintf('Loading %s\n', save_bg);
    load(save_bg, 'results');
    results_bg = results;
else
    results_bg = run_pa_sim(cfg_bg);
    results = results_bg;
    save(save_bg, 'results', '-v7.3');
    fprintf('Saved: %s\n', save_bg);
end

% =========================================================================
% Compute SBR
% =========================================================================
sbr = compute_sbr(results_with, results_bg);

fprintf('\n--- SBR Results ---\n');
fprintf('  Peak signal     : %.2f Pa\n', sbr.p_signal);
fprintf('  Peak background : %.2f Pa\n', sbr.p_background);
fprintf('  SBR             : %.2f\n',    sbr.value);
fprintf('  SBR             : %.1f dB\n', sbr.dB);

% =========================================================================
% Visualize
% =========================================================================
visualize_pa(results_with);
visualize_pa(results_bg);
