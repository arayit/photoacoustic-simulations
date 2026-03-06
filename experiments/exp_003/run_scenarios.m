clearvars; close all; clc;

% =========================================================================
% exp_003 — OR-PAM imaging scan
%
% Single BODIPY-TR target at y = 0, z = 3 mm, r = 5 um.
% Beam scanned from -65 to +65 um at 2 um steps (66 positions).
%
% 3 illumination scenarios (same physics as exp_002):
%   s01_ns    : NS single pulse  (tau = 3 ns,   F = 13.2 J/cm^2)
%   s02_fs    : FS single pulse  (tau = 100 fs, F = 1    J/cm^2)
%   s03_b300  : FS burst N=300   (tau = 100 fs, F = 1    J/cm^2 per pulse)
%
% Total: 3 x 66 = 198 runs
% =========================================================================

study_dir   = fileparts(mfilename('fullpath'));
addpath(fullfile(study_dir, '..', '..', 'engine'));
results_dir = fullfile(study_dir, 'results');
if ~exist(results_dir, 'dir'), mkdir(results_dir); end

force_rerun = false;

% --- Scan parameters ---
y_scan_list = (-65:2:65) * 1e-6;       % beam scan positions [m]
n_scan      = numel(y_scan_list);       % 66 positions

% --- Scenario definitions ---
%   Fields: prefix, pulse_duration, fluence_focus, burst_N, burst_tau
scen(1).prefix         = 's01_ns';
scen(1).pulse_duration = 3e-9;         % [s]
scen(1).fluence_focus  = 13.2;         % [J/cm^2]
scen(1).burst_N        = 1;
scen(1).burst_tau      = [];

scen(2).prefix         = 's02_fs';
scen(2).pulse_duration = 100e-15;      % [s]
scen(2).fluence_focus  = 1;            % [J/cm^2]
scen(2).burst_N        = 1;
scen(2).burst_tau      = [];

N_burst                = 300;
taup                   = 100e-15;      % per-pulse duration [s]
Fp                     = 1;            % per-pulse fluence  [J/cm^2]
scen(3).prefix         = sprintf('s03_b%03d', N_burst);
scen(3).pulse_duration = taup * N_burst;
scen(3).fluence_focus  = Fp  * N_burst;
scen(3).burst_N        = N_burst;
scen(3).burst_tau      = 3e-9;         % burst window [s]

n_scen  = numel(scen);
n_total = n_scen * n_scan;
sidx    = 0;
t_runs  = [];
t_start = tic;

fprintf('=== exp_003 | %d scenarios x %d positions = %d runs | %s ===\n\n', ...
    n_scen, n_scan, n_total, datestr(now, 'yyyy-mm-dd HH:MM:SS'));

% =========================================================================
% Base cfg — shared across all scenarios
% =========================================================================
base.lambda        = 1064e-9;
base.NA            = 0.55;
base.n             = 1.33;
base.target_depth  = 3e-3;             % [m]
base.target_radius = 5e-6;             % [m]
base.Gamma         = 0.12;

base.mu_a_tissue   = 18;               % [m^-1]
base.mu_s_tissue   = 91;               % [m^-1]

% BODIPY-TR: no linear absorption, TPA only
base.mu_a_target   = 0;
base.mu_s_target   = 0;
base.alpha2_target = 9e-14;            % [m/W]
base.alpha3_target = 0;

base.c_sound       = 1500;             % [m/s]
base.rho           = 1000;             % [kg/m^3]
base.alpha_coeff   = 0.75;             % [dB/MHz^y/cm]
base.alpha_power   = 1.5;

base.f_grid  = 50e6;             % [Hz]
base.PPW_acoustic  = 10;
base.n_elements    = 128;

base.z_max         = 6e-3;             % [m]
base.y_max         = 1.5e-3;           % [m]
base.PPW_optical   = 5;
base.opt_margin    = 5;
base.pml_size      = 40;
base.verbose       = false;

% =========================================================================
% Main loop
% =========================================================================
for is = 1:n_scen
    for k = 1:n_scan
        sidx   = sidx + 1;
        y_scan = y_scan_list(k);

        % label encodes scenario and scan position in um
        y_um = round(y_scan * 1e6);
        if y_um >= 0
            y_str = sprintf('p%03d', y_um);
        else
            y_str = sprintf('n%03d', abs(y_um));
        end

        cfg                = base;
        cfg.label          = [scen(is).prefix '_y_' y_str];
        cfg.pulse_duration = scen(is).pulse_duration;
        cfg.fluence_focus  = scen(is).fluence_focus;
        cfg.beam_y_center  = y_scan;    % beam moves
        cfg.target_y       = 0;         % target fixed at centre

        if scen(is).burst_N > 1
            cfg.burst_N   = scen(is).burst_N;
            cfg.burst_tau = scen(is).burst_tau;
        end

        save_path = fullfile(results_dir, [cfg.label '.mat']);
        fprintf('[%03d/%03d] %s ', sidx, n_total, cfg.label);
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
