clear all; close all; clc;

% --- Beam parameters ---
lambda         = 1064e-9;       % wavelength [m]
NA             = 0.55;          % numerical aperture (Mitutoyo Plan Apo)
n              = 1.33;          % refractive index (water/tissue)
target_depth   = 3e-3;          % focal depth [m]
target_radius  = 5e-6;          % target radius [m]

% --- Input radiation ---
fluence_focus  = 20;            % peak fluence at focus [J/cm^2]
pulse_duration = 5e-9;          % pulse duration [s]

% --- Gruneisen parameter ---
Gamma = 0.12;

% --- Tissue optical properties @ 1064 nm [m^-1] ---
mu_a_tissue = 18;
mu_s_tissue = 91;               % reduced scattering
mu_t_tissue = mu_a_tissue + mu_s_tissue;

% --- Target optical properties [m^-1] ---
mu_a_target = 500;
mu_s_target = 10;
mu_t_target = mu_a_target + mu_s_target;

% --- Beam ---
beam           = gaussian_beam_params(lambda, NA, n, target_depth);
I_focus_peak   = (fluence_focus * 1e4) / pulse_duration;            % [W/m^2]
I_surface_peak = I_focus_peak * (beam.w0 / beam.w_surface)^2;       % [W/m^2]

% --- Acoustic grid (matched to transducer bandwidth) ---
c_sound        = 1500;          % [m/s] - placeholder until medium is defined
f_transducer   = 50e6;          % transducer center frequency [Hz]
PPW_acoustic   = 10;            % points per wavelength
dx_acoustic    = c_sound / (f_transducer * PPW_acoustic);

% --- Global grid (Beer-Lambert + k-Wave) ---
z_max     = 4e-3;
y_max     = 1.5e-3;
Nz        = round(z_max / dx_acoustic);
Ny        = round(2*y_max / dx_acoustic);
z_vec     = linspace(0, z_max, Nz);
y_vec     = linspace(-y_max, y_max, Ny);

% --- Optical grid (local, around focal region) ---
PPW_optical  = 5;
dz_optical   = beam.zR / PPW_optical;      % axial: resolve Rayleigh range [m]
dy_optical   = beam.w0 / PPW_optical;      % lateral: resolve beam waist [m]
opt_margin   = 5;                           % half-extent in multiples of target_radius
opt_half_ext = opt_margin * target_radius;

z_opt_vec = linspace(target_depth - opt_half_ext, target_depth + opt_half_ext, ...
                     round(2*opt_half_ext / dz_optical));
y_opt_vec = linspace(-opt_half_ext, opt_half_ext, ...
                     round(2*opt_half_ext / dy_optical));

% --- Property maps on global grid ---
[mu_a_map, mu_t_map] = build_property_maps(z_vec, y_vec, ...
    mu_a_tissue, mu_t_tissue, mu_a_target, mu_t_target, target_depth, target_radius);

% --- Intensity on global grid (Beer-Lambert) ---
[I_map, acc_att_vec] = build_intensity_map(beam, z_vec, y_vec, I_surface_peak, mu_t_map);

% --- Intensity on optical grid ---
acc_att_opt = interp1(z_vec, acc_att_vec, z_opt_vec, 'linear');
I_opt_map   = zeros(length(z_opt_vec), length(y_opt_vec));
for iz = 1:length(z_opt_vec)
    delta_z           = z_opt_vec(iz) - beam.z_focus;
    w_z               = beam.w0 * sqrt(1 + (delta_z / beam.zR)^2);
    I_opt_map(iz, :)  = I_surface_peak * (beam.w_surface / w_z)^2 ...
                        .* exp(-2 * y_opt_vec.^2 / w_z^2) * exp(-acc_att_opt(iz));
end

% --- Property maps on optical grid ---
[mu_a_opt_map, ~] = build_property_maps(z_opt_vec, y_opt_vec, ...
    mu_a_tissue, mu_t_tissue, mu_a_target, mu_t_target, target_depth, target_radius);

% --- Energy deposition and initial pressure on optical grid ---
Q_opt  = mu_a_opt_map .* I_opt_map * pulse_duration;   % [J/m^3]
p0_opt = Gamma * Q_opt;                                 % [Pa]

% --- Interpolate p0 to acoustic grid ---
[Z_opt, Y_opt] = ndgrid(z_opt_vec, y_opt_vec);
[Z_ac,  Y_ac]  = ndgrid(z_vec, y_vec);
F           = griddedInterpolant(Z_opt, Y_opt, p0_opt, 'linear', 'none');
p0_acoustic = F(Z_ac, Y_ac);
p0_acoustic(isnan(p0_acoustic)) = 0;

fprintf('Beam:\n');
fprintf('  w0          = %.3f um\n', beam.w0*1e6);
fprintf('  zR          = %.3f um\n', beam.zR*1e6);
fprintf('  w_surf      = %.2f mm\n', beam.w_surface*1e3);
fprintf('  I_focus     = %.2e W/m^2\n', I_focus_peak);
fprintf('  I_surface   = %.2e W/m^2\n', I_surface_peak);
fprintf('\nGlobal grid:  %d x %d pts  (dx = %.1f um)\n', Nz, Ny, dx_acoustic*1e6);
fprintf('Optical grid: %d x %d pts  (dz = %.0f nm, dy = %.0f nm)\n', ...
    length(z_opt_vec), length(y_opt_vec), dz_optical*1e9, dy_optical*1e9);
