clear all; close all; clc;

show_plots = true;

% --- Beam parameters ---
lambda         = 1064e-9;       % wavelength [m]
NA             = 0.55;          % numerical aperture (Mitutoyo Plan Apo)
n              = 1.33;          % refractive index (water/tissue)
target_depth   = 3e-3;          % focal depth [m]
target_radius  = 5e-6;          % target radius [m]

% --- Input radiation ---
fluence        = 20;            % surface fluence [J/cm^2]
pulse_duration = 5e-9;          % pulse duration [s]

% --- Beam ---
beam           = gaussian_beam_params(lambda, NA, n, target_depth);
I_surface_peak = (fluence * 1e4) / pulse_duration;  % [W/m^2]

% --- Acoustic grid (matched to target characteristic frequency) ---
c_sound       = 1500;           % [m/s] - placeholder until medium is defined
PPW_acoustic  = 10;             % points per wavelength
f_char        = c_sound / (2 * target_radius);
dx_acoustic   = c_sound / (f_char * PPW_acoustic);

% --- Optical grid (to resolve beam waist at focus) ---
PPW_optical   = 5;              % points across beam waist
dy_optical    = beam.w0 / PPW_optical;

fprintf('Beam:\n');
fprintf('  w0          = %.3f um\n', beam.w0*1e6);
fprintf('  zR          = %.3f um\n', beam.zR*1e6);
fprintf('  w_surf      = %.2f mm\n', beam.w_surface*1e3);
fprintf('  I_surface   = %.2e W/m^2\n', I_surface_peak);
fprintf('\nGrid:\n');
fprintf('  f_char      = %.1f MHz\n', f_char*1e-6);
fprintf('  dx_acoustic = %.2f um\n', dx_acoustic*1e6);
fprintf('  dy_optical  = %.1f nm\n', dy_optical*1e9);
