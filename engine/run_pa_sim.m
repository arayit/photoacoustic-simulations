function results = run_pa_sim(cfg)
% RUN_PA_SIM  Run photoacoustic simulation.
%
%   results = run_pa_sim(cfg)
%
%   See scenario_baseline.m for a complete cfg example.

% --- Validate ---
validate_cfg(cfg);

% --- Unpack cfg ---
lambda         = cfg.lambda;
NA             = cfg.NA;
n              = cfg.n;
target_depth   = cfg.target_depth;
target_radius  = cfg.target_radius;

fluence_focus  = cfg.fluence_focus;
pulse_duration = cfg.pulse_duration;
Gamma          = cfg.Gamma;

mu_a_tissue    = cfg.mu_a_tissue;
mu_s_tissue    = cfg.mu_s_tissue;
mu_t_tissue    = mu_a_tissue + mu_s_tissue;

mu_a_target    = cfg.mu_a_target;
mu_s_target    = cfg.mu_s_target;
mu_t_target    = mu_a_target + mu_s_target;
alpha2_target  = cfg.alpha2_target;
alpha3_target  = cfg.alpha3_target;

c_sound        = cfg.c_sound;
rho            = cfg.rho;
alpha_coeff    = cfg.alpha_coeff;
alpha_power    = cfg.alpha_power;

f_transducer   = cfg.f_transducer;
PPW_acoustic   = cfg.PPW_acoustic;
n_elements     = cfg.n_elements;

z_max          = cfg.z_max;
y_max          = cfg.y_max;
PPW_optical    = cfg.PPW_optical;
opt_margin     = cfg.opt_margin;

verbose  = true;
if isfield(cfg, 'verbose'),  verbose  = cfg.verbose;  end
pml_size = 20;
if isfield(cfg, 'pml_size'), pml_size = cfg.pml_size; end
burst_N   = 1;
burst_tau = [];
f_R       = [];
if isfield(cfg, 'burst_N'),   burst_N   = cfg.burst_N;   end
if isfield(cfg, 'burst_tau'), burst_tau = cfg.burst_tau; end
if burst_N > 1
    f_R = burst_N / burst_tau;
end

beam_y_center = 0;
target_y      = 0;
if isfield(cfg, 'beam_y_center'), beam_y_center = cfg.beam_y_center; end
if isfield(cfg, 'target_y'),      target_y      = cfg.target_y;      end

% --- Beam ---
beam              = gaussian_beam_params(lambda, NA, n, target_depth);
fluence_focus_si  = fluence_focus * 1e4;            % J/cm² → J/m²
I_focus_peak      = fluence_focus_si / pulse_duration;
I_surface_peak    = I_focus_peak * (beam.w0 / beam.w_surface)^2;

% --- Acoustic grid ---
dx_acoustic    = c_sound / (f_transducer * PPW_acoustic);

% --- Global grid ---
Nz     = round(z_max / dx_acoustic);
Ny     = round(2*y_max / dx_acoustic);
z_vec  = linspace(0, z_max, Nz);
y_vec  = linspace(-y_max, y_max, Ny);

% --- Optical grid ---
dz_optical   = beam.zR / PPW_optical;
dy_optical   = beam.w0 / PPW_optical;
opt_half_ext = opt_margin * target_radius;
z_opt_vec    = linspace(target_depth - opt_half_ext, target_depth + opt_half_ext, ...
                        round(2*opt_half_ext / dz_optical));
y_opt_vec    = linspace(beam_y_center - opt_half_ext, beam_y_center + opt_half_ext, ...
                        round(2*opt_half_ext / dy_optical));

% --- Property maps on global grid ---
[~, mu_t_map] = build_property_maps(z_vec, y_vec, ...
    mu_a_tissue, mu_t_tissue, mu_a_target, mu_t_target, target_depth, target_radius, ...
    0, 0, 0, 0, target_y);

% --- Intensity on global grid (Beer-Lambert) ---
[I_map, acc_att_vec] = build_intensity_map(beam, z_vec, y_vec, I_surface_peak, mu_t_map, beam_y_center);

% --- Intensity on optical grid ---
acc_att_opt = interp1(z_vec, acc_att_vec, z_opt_vec, 'linear');
I_opt_map   = zeros(length(z_opt_vec), length(y_opt_vec));
for iz = 1:length(z_opt_vec)
    delta_z          = z_opt_vec(iz) - beam.z_focus;
    w_z              = beam.w0 * sqrt(1 + (delta_z / beam.zR)^2);
    I_opt_map(iz, :) = I_surface_peak * (beam.w_surface / w_z)^2 ...
                       .* exp(-2 * (y_opt_vec - beam_y_center).^2 / w_z^2) * exp(-acc_att_opt(iz));
end

% --- Property maps on optical grid ---
[mu_a_opt_map, ~, alpha2_opt_map, alpha3_opt_map] = build_property_maps(z_opt_vec, y_opt_vec, ...
    mu_a_tissue, mu_t_tissue, mu_a_target, mu_t_target, target_depth, target_radius, ...
    0, alpha2_target, 0, alpha3_target, target_y);

% --- Energy deposition and initial pressure on optical grid ---
Q_opt  = burst_N * (mu_a_opt_map .* I_opt_map ...
        + alpha2_opt_map .* I_opt_map.^2 ...
        + alpha3_opt_map .* I_opt_map.^3) * pulse_duration;
p0_opt = Gamma * Q_opt;

% --- Interpolate p0 to acoustic grid ---
[Z_opt, Y_opt] = ndgrid(z_opt_vec, y_opt_vec);
[Z_ac,  Y_ac]  = ndgrid(z_vec, y_vec);
F           = griddedInterpolant(Z_opt, Y_opt, p0_opt, 'linear', 'none');
p0_acoustic = F(Z_ac, Y_ac);
p0_acoustic(isnan(p0_acoustic)) = 0;

if verbose
    fprintf('Beam:\n');
    fprintf('  w0          = %.3f um\n', beam.w0*1e6);
    fprintf('  zR          = %.3f um\n', beam.zR*1e6);
    fprintf('  w_surf      = %.2f mm\n', beam.w_surface*1e3);
    fprintf('  I_focus     = %.2e W/m^2\n', I_focus_peak);
    fprintf('  I_surface   = %.2e W/m^2\n', I_surface_peak);
    if beam_y_center ~= 0 || target_y ~= 0
        fprintf('Scanning:\n');
        fprintf('  beam_y      = %.1f um\n', beam_y_center*1e6);
        fprintf('  target_y    = %.1f um\n', target_y*1e6);
    end
    if burst_N > 1
        fprintf('Burst mode:\n');
        fprintf('  N           = %d pulses\n', burst_N);
        fprintf('  tau_burst   = %.1f ns\n', burst_tau*1e9);
        fprintf('  f_R         = %.2f GHz\n', f_R*1e-9);
    end
    fprintf('\nGlobal grid:  %d x %d pts  (dx = %.1f um)\n', Nz, Ny, dx_acoustic*1e6);
    fprintf('Optical grid: %d x %d pts  (dz = %.0f nm, dy = %.0f nm)\n', ...
        length(z_opt_vec), length(y_opt_vec), dz_optical*1e9, dy_optical*1e9);
end

% --- k-Wave grid ---
kgrid = kWaveGrid(Nz, dx_acoustic, Ny, dx_acoustic);

% --- k-Wave medium ---
medium.sound_speed = c_sound;
medium.density     = rho;
medium.alpha_coeff = alpha_coeff;
medium.alpha_power = alpha_power;

% --- Source ---
source.p0 = p0_acoustic;

% --- Sensor: linear array at tissue surface ---
element_pitch = c_sound / (2 * f_transducer);
element_y     = linspace(-(n_elements-1)/2, (n_elements-1)/2, n_elements) * element_pitch;
element_iy    = round((element_y - y_vec(1)) / dx_acoustic) + 1;
element_iy    = max(1, min(Ny, element_iy));
sensor.mask   = zeros(Nz, Ny);
sensor.mask(1, element_iy) = 1;

% --- Time array ---
t_end = 2 * z_max / c_sound;
kgrid.makeTime(c_sound, [], t_end);

% --- GPU ---
if gpuDeviceCount > 0
    data_cast = 'gpuArray-single';
    if verbose, fprintf('\nGPU detected: %s\n', gpuDevice().Name); end
else
    data_cast = 'single';
    if verbose, fprintf('\nNo GPU detected, running on CPU.\n'); end
end

% --- Run k-Wave ---
if verbose, fprintf('Running k-Wave...\n'); end
sensor_data = kspaceFirstOrder2D(kgrid, medium, source, sensor, ...
    'PMLSize', pml_size, 'PlotSim', false, 'DataCast', data_cast);

if gpuDeviceCount > 0
    sensor_data = gather(sensor_data);
end

if verbose
    fprintf('Done. Sensor data: %d elements x %d time steps\n', ...
        size(sensor_data, 1), size(sensor_data, 2));
end

% --- Pack results ---
results.sensor_data  = sensor_data;
if burst_N > 1
    results.burst_N   = burst_N;
    results.burst_tau = burst_tau;
    results.burst_fR  = f_R;
end
results.t_array      = kgrid.t_array;   % plain double — load without k-Wave
results.kgrid        = kgrid;
results.p0_acoustic  = p0_acoustic;
results.p0_opt       = p0_opt;
results.Q_opt        = Q_opt;
results.I_opt_map    = I_opt_map;
results.I_map        = I_map;
results.beam         = beam;
results.z_vec        = z_vec;
results.y_vec        = y_vec;
results.z_opt_vec    = z_opt_vec;
results.y_opt_vec    = y_opt_vec;
results.element_y    = element_y;
results.cfg          = cfg;
if beam_y_center ~= 0 || target_y ~= 0
    results.beam_y_center = beam_y_center;
    results.target_y      = target_y;
end
