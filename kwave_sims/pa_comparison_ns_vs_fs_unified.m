% =========================================================================
% PHOTOACOUSTIC IMAGING COMPARISON: NS vs FS BURST
% UNIFIED SIMULATION FILE
% =========================================================================
% This script compares:
%   1. Single Nanosecond (NS) pulse
%   2. Femtosecond (FS) burst (N pulses, burst duration = NS pulse duration)
%
% Beam: Gaussian, focused at target location
% Input: Surface fluence [J/cm^2], intensity increases with focusing
% =========================================================================

clear all;
close all;
clc;

%% ========================================================================
%                    USER CONFIGURABLE PARAMETERS
% =========================================================================

% --- Geometry ---
target_depth = 300e-6;      % Target center depth [m] (focal point)
target_radius = 5e-6;       % Target radius [m]
z_max = 600e-6;             % Total simulation depth [m]
y_max = 50e-6;              % Lateral extent [m] (+/-)

% --- Fluence Inputs [J/cm^2] AT FOCUS ---
fluence_ns_at_focus = 20/10;             % NS pulse fluence at focus [J/cm^2]
fluence_fs_per_pulse_at_focus = 1.2/10;   % FS per-pulse fluence at focus [J/cm^2]

% --- Pulse Timing ---
pulse_duration_ns = 5e-9;       % NS pulse duration [s]
pulse_duration_fs = 100e-15;    % FS pulse duration [s]
rep_rate_intra_burst = 100e9;   % Intra-burst repetition rate [Hz]
rep_rate_laser_Hz = 1000;       % Laser repetition rate [Hz]

% --- Contrast Agent Selection ---
% Options: 'MoS2', 'RhodamineB', 'Rhodamine101', 'BODIPY'
contrast_agent = 'BODIPY';

%% ========================================================================
%                    WAVELENGTH AND BEAM PARAMETERS
% =========================================================================

lambda = 1064e-9;           % Wavelength [m] - NIR-II window
NA = 0.65;                  % Numerical aperture
n = 1.33;                   % Refractive index (water/tissue)

% Derived beam parameters
w0 = lambda / (pi * NA);    % Beam waist at focus [m]
zR = pi * w0^2 / lambda;    % Rayleigh range [m]
z_focus = target_depth;     % Focus at target

% Beam radius at surface (for focused beam)
w_surface = w0 * sqrt(1 + (z_focus/zR)^2);

%% ========================================================================
%                    TISSUE OPTICAL PROPERTIES
% =========================================================================
% Source: Ritz et al. 2001, "Optical properties of native and coagulated 
%         porcine liver tissue between 400 and 2400 nm"

mu_a_tissue = 18;           % Linear absorption [m^-1]
mu_s_prime_tissue = 91;     % Reduced scattering [m^-1]
mu_t_tissue = mu_a_tissue + mu_s_prime_tissue;  % Total attenuation [m^-1]

%% ========================================================================
%                    TARGET OPTICAL PROPERTIES
% =========================================================================

mu_a_target = 50;           % Linear absorption [m^-1]
mu_s_prime_target = 10;     % Reduced scattering [m^-1]
mu_t_target = mu_a_target + mu_s_prime_target;

%% ========================================================================
%                    TPA COEFFICIENT CALCULATION
% =========================================================================

% Physical constants
h_planck = 6.626e-34;       % Planck constant [J*s]
c_speed = 3.0e8;            % Speed of light [m/s]
E_photon = (h_planck * c_speed) / lambda;  % Photon energy [J]
N_A = 6.022e23;             % Avogadro's number [mol^-1]

% GM to SI conversion factor [m^4/W]
GM_to_SI = 1e-58 / E_photon;

% --- MoS2 Quantum Dots ---
% Source: Jones et al. 2017
C_QD = 200;                     % QD concentration [ug/mL]
sigma_TPA_GM_MoS2 = 58960;      % Cross-section [GM]
MW_QD = 1e5;                    % Molecular weight [g/mol]
N_QD = (C_QD * 1e-6 * 1e6 * N_A) / MW_QD;  % Number density [m^-3]
sigma_TPA_MoS2_SI = sigma_TPA_GM_MoS2 * GM_to_SI;
alpha_2_MoS2 = sigma_TPA_MoS2_SI * N_QD;   % [m/W]

% --- Organic Dyes (50 uM concentration) ---
C_Dye_uM = 50;
N_Dye = C_Dye_uM * 1e-3 * N_A;  % Number density [m^-3]

% Rhodamine B (Makarov et al. 2008)
sigma_GM_RhoB = 39;
alpha_2_RhoB = sigma_GM_RhoB * GM_to_SI * N_Dye;

% Rhodamine 101 (Li and She 2010)
sigma_GM_Rho101 = 20;
alpha_2_Rho101 = sigma_GM_Rho101 * GM_to_SI * N_Dye;

% BODIPY-TR (Mutze et al. 2012)
sigma_GM_Bodipy = 242;
% alpha_2_Bodipy = sigma_GM_Bodipy * GM_to_SI * N_Dye;
alpha_2_Bodipy = 9e-13;
% Select contrast agent
switch contrast_agent
    case 'MoS2'
        alpha_2_target = alpha_2_MoS2;
    case 'RhodamineB'
        alpha_2_target = alpha_2_RhoB;
    case 'Rhodamine101'
        alpha_2_target = alpha_2_Rho101;
    case 'BODIPY'
        alpha_2_target = alpha_2_Bodipy;
    otherwise
        error('Unknown contrast agent: %s', contrast_agent);
end

%% ========================================================================
%                    CALCULATED BURST PARAMETERS
% =========================================================================

% Number of pulses: burst duration = NS pulse duration
burst_duration = pulse_duration_ns;
N_pulses_fs = round(burst_duration * rep_rate_intra_burst);

% Total FS burst fluence at focus
fluence_fs_total_at_focus = fluence_fs_per_pulse_at_focus * N_pulses_fs;

%% ========================================================================
%                    FLUENCE CONVERSION: FOCUS TO SURFACE
% =========================================================================
% The beam expands from w0 (at focus) to w_surface (at tissue surface)
% Energy conservation: F_surface * A_surface = F_focus * A_focus
% Therefore: F_surface = F_focus * (w0/w_surface)^2

focusing_factor = (w_surface / w0)^2;  % Intensity gain from surface to focus

% Convert focal fluence to surface fluence
fluence_ns_surface = fluence_ns_at_focus / focusing_factor;           % [J/cm^2]
fluence_fs_per_pulse_surface = fluence_fs_per_pulse_at_focus / focusing_factor;  % [J/cm^2]
fluence_fs_total_surface = fluence_fs_total_at_focus / focusing_factor;

% Convert to SI [J/m^2]
fluence_ns_surface_SI = fluence_ns_surface * 1e4;           % [J/m^2]
fluence_fs_per_pulse_SI = fluence_fs_per_pulse_surface * 1e4;  % [J/m^2]

% Also store focal fluence in SI
fluence_ns_at_focus_SI = fluence_ns_at_focus * 1e4;           % [J/m^2]
fluence_fs_per_pulse_at_focus_SI = fluence_fs_per_pulse_at_focus * 1e4;  % [J/m^2]

%% ========================================================================
%                    PRINT CONFIGURATION
% =========================================================================

fprintf('=================================================================\n');
fprintf('   PA IMAGING COMPARISON: NS vs FS BURST\n');
fprintf('   UNIFIED SIMULATION\n');
fprintf('=================================================================\n\n');

fprintf('Geometry:\n');
fprintf('  Target depth (focal point): %.0f um\n', target_depth*1e6);
fprintf('  Target radius: %.0f um\n', target_radius*1e6);
fprintf('  Simulation depth: %.0f um\n', z_max*1e6);
fprintf('  Lateral extent: +/-%.0f um\n\n', y_max*1e6);

fprintf('Beam Parameters:\n');
fprintf('  Wavelength: %.0f nm\n', lambda*1e9);
fprintf('  NA: %.2f\n', NA);
fprintf('  Beam waist w0: %.3f um\n', w0*1e6);
fprintf('  Rayleigh range zR: %.3f um\n', zR*1e6);
fprintf('  Spot radius at surface: %.1f um\n\n', w_surface*1e6);

fprintf('Pulse Configuration:\n');
fprintf('  NS pulse duration: %.1f ns\n', pulse_duration_ns*1e9);
fprintf('  FS pulse duration: %.0f fs\n', pulse_duration_fs*1e15);
fprintf('  Intra-burst rep rate: %.0f GHz\n', rep_rate_intra_burst*1e-9);
fprintf('  Burst duration: %.1f ns (= NS pulse duration)\n', burst_duration*1e9);
fprintf('  Number of FS pulses (N): %d\n\n', N_pulses_fs);

fprintf('Fluence Settings (INPUT AT FOCUS):\n');
fprintf('  NS fluence at focus: %.2e J/cm^2\n', fluence_ns_at_focus);
fprintf('  FS per-pulse at focus: %.2e J/cm^2\n', fluence_fs_per_pulse_at_focus);
fprintf('  FS total burst at focus: %.2e J/cm^2\n', fluence_fs_total_at_focus);
fprintf('  ------------------------------------------------\n');
fprintf('  Focusing factor: %.2e (w_surface/w0)^2\n', focusing_factor);
fprintf('  ------------------------------------------------\n');
fprintf('  NS fluence at surface: %.2e J/cm^2\n', fluence_ns_surface);
fprintf('  FS per-pulse at surface: %.2e J/cm^2\n', fluence_fs_per_pulse_surface);
fprintf('  FS total burst at surface: %.2e J/cm^2\n\n', fluence_fs_total_surface);

fprintf('Contrast Agent: %s\n', contrast_agent);
fprintf('  TPA coefficient: %.2e m/W\n\n', alpha_2_target);

%% ========================================================================
%                    GRID SETUP
% =========================================================================

z_points = round(z_max / 0.5e-6);   % dz ~ 0.5 um
y_points = round(2*y_max / 0.2e-6); % dy ~ 0.2 um

dz = z_max / z_points;
dy = 2*y_max / y_points;

z_vec = linspace(0, z_max, z_points);
y_vec = linspace(-y_max, y_max, y_points);

% Resolution check
points_across_w0 = w0 / dy;
points_across_target = 2*target_radius / dy;

fprintf('Grid Resolution:\n');
fprintf('  Depth: 0 to %.0f um (%d points, dz = %.2f um)\n', z_max*1e6, z_points, dz*1e6);
fprintf('  Lateral: +/-%.0f um (%d points, dy = %.2f um)\n', y_max*1e6, y_points, dy*1e6);
fprintf('  Points across w0: %.1f\n', points_across_w0);
fprintf('  Points across target: %.1f\n\n', points_across_target);

if points_across_w0 < 5
    warning('Lateral resolution may be insufficient for beam waist!');
end

%% ========================================================================
%                    CREATE PROPERTY MAPS
% =========================================================================

mu_a_map = mu_a_tissue * ones(z_points, y_points);
mu_t_map = mu_t_tissue * ones(z_points, y_points);
alpha_2_map = zeros(z_points, y_points);

for iz = 1:z_points
    z = z_vec(iz);
    for iy = 1:y_points
        y = y_vec(iy);
        dist = sqrt((z - target_depth)^2 + y^2);
        if dist <= target_radius
            mu_a_map(iz, iy) = mu_a_target;
            mu_t_map(iz, iy) = mu_t_target;
            alpha_2_map(iz, iy) = alpha_2_target;
        end
    end
end

%% ========================================================================
%                    POWER & ENERGY CALCULATION
% =========================================================================

% Effective Gaussian beam area at focus
beam_area_focus_m2 = (pi * w0^2) / 2;

% Energy per pulse (calculated from focal fluence)
energy_ns_per_pulse = fluence_ns_at_focus_SI * beam_area_focus_m2;
energy_fs_per_pulse = fluence_fs_per_pulse_at_focus_SI * beam_area_focus_m2;
energy_fs_per_burst = energy_fs_per_pulse * N_pulses_fs;

% Average power
avg_power_ns = energy_ns_per_pulse * rep_rate_laser_Hz;
avg_power_fs = energy_fs_per_burst * rep_rate_laser_Hz;

fprintf('Power & Energy:\n');
fprintf('  Beam area at focus: %.2e m^2 (w0 = %.3f um)\n', beam_area_focus_m2, w0*1e6);
fprintf('  NS energy per pulse: %.2e J (%.2f nJ)\n', energy_ns_per_pulse, energy_ns_per_pulse*1e9);
fprintf('  FS energy per pulse: %.2e J (%.2f nJ)\n', energy_fs_per_pulse, energy_fs_per_pulse*1e9);
fprintf('  FS energy per burst: %.2e J (%.2f nJ)\n', energy_fs_per_burst, energy_fs_per_burst*1e9);
fprintf('  NS average power: %.3f uW\n', avg_power_ns*1e6);
fprintf('  FS average power: %.3f uW\n\n', avg_power_fs*1e6);

%% ========================================================================
%                    CASE 1: NANOSECOND PULSE
% =========================================================================

fprintf('=================================================================\n');
fprintf('CASE 1: NANOSECOND PULSE\n');
fprintf('=================================================================\n');

tau_ns = pulse_duration_ns;

% Initialize maps
I_map_ns = zeros(z_points, y_points);
Q_linear_map_ns = zeros(z_points, y_points);
Q_TPA_map_ns = zeros(z_points, y_points);

% Surface intensity
I_surface_peak_ns = fluence_ns_surface_SI / tau_ns;
I_focus_peak_ns = fluence_ns_at_focus_SI / tau_ns;

fprintf('  Surface peak intensity: %.2e W/m^2\n', I_surface_peak_ns);
fprintf('  Focal peak intensity: %.2e W/m^2\n', I_focus_peak_ns);

% Beam propagation
accumulated_attenuation_ns = 0;

for iz = 1:z_points
    z = z_vec(iz);
    delta_z = z - z_focus;
    w_z = w0 * sqrt(1 + (delta_z/zR)^2);
    
    % Focusing factor (intensity increases as beam converges)
    focusing_factor = (w_surface / w_z)^2;
    
    % Peak intensity at depth
    I_peak_at_depth = I_surface_peak_ns * focusing_factor * exp(-accumulated_attenuation_ns);
    
    % Gaussian lateral profile
    intensity_current = I_peak_at_depth * exp(-2 * y_vec.^2 / w_z^2);
    I_map_ns(iz, :) = intensity_current;
    
    % Energy deposition
    Q_linear_map_ns(iz, :) = mu_a_map(iz, :) .* intensity_current * tau_ns;
    Q_TPA_map_ns(iz, :) = alpha_2_map(iz, :) .* (intensity_current.^2) * tau_ns;
    
    % Update attenuation
    if iz < z_points
        avg_mu_t = sum(mu_t_map(iz, :) .* intensity_current) / sum(intensity_current);
        avg_alpha2_I = sum(alpha_2_map(iz, :) .* intensity_current.^2) / sum(intensity_current);
        accumulated_attenuation_ns = accumulated_attenuation_ns + (avg_mu_t + avg_alpha2_I) * dz;
    end
end

Q_total_map_ns = Q_linear_map_ns + Q_TPA_map_ns;
Q_linear_total_ns = sum(Q_linear_map_ns(:)) * dz * dy;
Q_TPA_total_ns = sum(Q_TPA_map_ns(:)) * dz * dy;
E_ns_total = Q_linear_total_ns + Q_TPA_total_ns;

fprintf('  Energy deposited: %.3e J\n', E_ns_total);
fprintf('    Linear: %.1f%%\n', 100*Q_linear_total_ns/E_ns_total);
fprintf('    TPA: %.1f%%\n', 100*Q_TPA_total_ns/E_ns_total);

% Thermal parameters
gamma_gruneisen = 0.12;

% Initial pressure
p0_map_ns = gamma_gruneisen * Q_total_map_ns;
p0_max_ns = max(p0_map_ns(:));
fprintf('  Max initial pressure: %.2f Pa\n\n', p0_max_ns);

%% ========================================================================
%                    CASE 2: FEMTOSECOND BURST
% =========================================================================

fprintf('=================================================================\n');
fprintf('CASE 2: FEMTOSECOND BURST\n');
fprintf('=================================================================\n');

tau_fs = pulse_duration_fs;

% Initialize maps
I_map_fs = zeros(z_points, y_points);
Q_linear_map_fs = zeros(z_points, y_points);
Q_TPA_map_fs = zeros(z_points, y_points);

% Surface intensity per pulse
I_surface_peak_fs = fluence_fs_per_pulse_SI / tau_fs;
I_focus_peak_fs = fluence_fs_per_pulse_at_focus_SI / tau_fs;

fprintf('  Surface peak intensity (per pulse): %.2e W/m^2\n', I_surface_peak_fs);
fprintf('  Focal peak intensity (per pulse): %.2e W/m^2\n', I_focus_peak_fs);

% Beam propagation
accumulated_attenuation_fs = 0;

for iz = 1:z_points
    z = z_vec(iz);
    delta_z = z - z_focus;
    w_z = w0 * sqrt(1 + (delta_z/zR)^2);
    
    % Focusing factor
    focusing_factor = (w_surface / w_z)^2;
    
    % Peak intensity at depth
    I_peak_at_depth = I_surface_peak_fs * focusing_factor * exp(-accumulated_attenuation_fs);
    
    % Gaussian lateral profile
    intensity_current = I_peak_at_depth * exp(-2 * y_vec.^2 / w_z^2);
    I_map_fs(iz, :) = intensity_current;
    
    % Energy deposition per pulse
    Q_linear_map_fs(iz, :) = mu_a_map(iz, :) .* intensity_current * tau_fs;
    Q_TPA_map_fs(iz, :) = alpha_2_map(iz, :) .* (intensity_current.^2) * tau_fs;
    
    % Update attenuation
    if iz < z_points
        avg_mu_t = sum(mu_t_map(iz, :) .* intensity_current) / sum(intensity_current);
        avg_alpha2_I = sum(alpha_2_map(iz, :) .* intensity_current.^2) / sum(intensity_current);
        accumulated_attenuation_fs = accumulated_attenuation_fs + (avg_mu_t + avg_alpha2_I) * dz;
    end
end

% Total energy deposition for entire burst
Q_total_map_fs = (Q_linear_map_fs + Q_TPA_map_fs) * N_pulses_fs;
Q_linear_total_fs = sum(Q_linear_map_fs(:)) * dz * dy * N_pulses_fs;
Q_TPA_total_fs = sum(Q_TPA_map_fs(:)) * dz * dy * N_pulses_fs;
E_fs_total = Q_linear_total_fs + Q_TPA_total_fs;

fprintf('  Energy deposited (burst): %.3e J\n', E_fs_total);
fprintf('    Linear: %.1f%%\n', 100*Q_linear_total_fs/E_fs_total);
fprintf('    TPA: %.1f%%\n', 100*Q_TPA_total_fs/E_fs_total);

% Initial pressure
p0_map_fs = gamma_gruneisen * Q_total_map_fs;
p0_max_fs = max(p0_map_fs(:));
fprintf('  Max initial pressure: %.2f Pa\n\n', p0_max_fs);

%% ========================================================================
%                    ACOUSTIC PROPAGATION (k-Wave with GPU)
% =========================================================================

fprintf('=================================================================\n');
fprintf('ACOUSTIC PROPAGATION (GPU-accelerated)\n');
fprintf('=================================================================\n');

% Check GPU availability
if gpuDeviceCount > 0
    gpu_info = gpuDevice;
    fprintf('  GPU detected: %s\n', gpu_info.Name);
    fprintf('  Compute capability: %.1f\n', gpu_info.ComputeCapability);
    use_gpu = true;
else
    warning('No GPU detected. Running on CPU.');
    use_gpu = false;
end

% Create k-Wave grid
kgrid = kWaveGrid(z_points, dz, y_points, dy);

% Medium properties
medium.sound_speed = 1500;
medium.density = 1000;
medium.alpha_coeff = 0.75;
medium.alpha_power = 1.5;

% Sensor (line array near surface)
sensor_depth = 50e-6;
sensor_row = round(sensor_depth / dz);
sensor.mask = zeros(z_points, y_points);
sensor.mask(sensor_row, :) = 1;

% Time axis
t_end = 2 * z_max / medium.sound_speed;
kgrid.makeTime(medium.sound_speed, [], t_end);

fprintf('  Grid: %d x %d points\n', z_points, y_points);
fprintf('  Sensor depth: %.0f um\n', sensor_depth*1e6);
fprintf('  Simulation time: %.2f us\n\n', t_end*1e6);

% Set DataCast based on GPU availability
if use_gpu
    data_cast = 'gpuArray-single';
else
    data_cast = 'single';  % Still use single precision for speed
end

% Run k-Wave for NS pulse
fprintf('  Running k-Wave for NS pulse...\n');
source.p0 = p0_map_ns;
sensor_data_ns = kspaceFirstOrder2D(kgrid, medium, source, sensor, ...
    'PMLSize', 20, 'PlotSim', false, 'DataCast', data_cast);

% Run k-Wave for FS burst
fprintf('  Running k-Wave for FS burst...\n');
source.p0 = p0_map_fs;
sensor_data_fs = kspaceFirstOrder2D(kgrid, medium, source, sensor, ...
    'PMLSize', 20, 'PlotSim', false, 'DataCast', data_cast);

% Gather data from GPU if necessary
if use_gpu
    sensor_data_ns = gather(sensor_data_ns);
    sensor_data_fs = gather(sensor_data_fs);
end

fprintf('  k-Wave simulations complete!\n\n');

% Ensure correct format [time x sensors]
if size(sensor_data_ns, 2) == length(kgrid.t_array)
    sensor_data_ns = sensor_data_ns';
end
if size(sensor_data_fs, 2) == length(kgrid.t_array)
    sensor_data_fs = sensor_data_fs';
end

%% ========================================================================
%                    TIME-GATING
% =========================================================================

distance_to_target = target_depth - sensor_depth;
arrival_time = distance_to_target / medium.sound_speed;
gate_start_time = arrival_time - 0.02e-6;
gate_start_idx = find(kgrid.t_array >= gate_start_time, 1, 'first');
if isempty(gate_start_idx)
    gate_start_idx = 1;
end

% Apply time gate
sensor_data_ns_gated = sensor_data_ns;
sensor_data_ns_gated(1:gate_start_idx-1, :) = 0;

sensor_data_fs_gated = sensor_data_fs;
sensor_data_fs_gated(1:gate_start_idx-1, :) = 0;

fprintf('Time-gating: signals before t = %.3f us removed\n\n', gate_start_time*1e6);

%% ========================================================================
%                    ENHANCEMENT ANALYSIS
% =========================================================================

[~, center_idx] = min(abs(y_vec));
signal_ns = sensor_data_ns_gated(:, center_idx);
signal_fs = sensor_data_fs_gated(:, center_idx);

p2p_ns = max(signal_ns) - min(signal_ns);
p2p_fs = max(signal_fs) - min(signal_fs);

enhancement_factor = p2p_fs / p2p_ns;

fprintf('=================================================================\n');
fprintf('ENHANCEMENT ANALYSIS\n');
fprintf('=================================================================\n');
fprintf('  NS peak-to-peak: %.2e Pa\n', p2p_ns);
fprintf('  FS peak-to-peak: %.2e Pa\n', p2p_fs);
fprintf('  Enhancement factor: %.1fx\n\n', enhancement_factor);

%% ========================================================================
%                    VISUALIZATION
% =========================================================================

% Calculate peak powers
peak_power_ns = energy_ns_per_pulse / tau_ns;
peak_power_fs = energy_fs_per_pulse / tau_fs;
time_vec = kgrid.t_array(:);

% -------------------------------------------------------------------------
% FIGURE 1: Waveforms (comparison on top, individual below)
% -------------------------------------------------------------------------
figure('Position', [50, 50, 1000, 700]);

% Plot 1: Waveform Comparison (top, spanning full width)
subplot(2,2,[1 2]);
plot(time_vec*1e6, signal_ns, 'b-', 'LineWidth', 1.5);
hold on;
plot(time_vec*1e6, signal_fs, 'r-', 'LineWidth', 1.5);
hold off;
xlabel('Time [us]');
ylabel('Pressure [Pa]');
title('Waveform Comparison', 'FontWeight', 'bold');
legend('NS', 'FS', 'Location', 'northeast');
grid on;
xlim([gate_start_time*1e6, max(kgrid.t_array)*1e6]);

overlay_stats = {sprintf('\\bfBurst Configuration:\\rm'), ...
                 sprintf('Intra-burst Rep Rate: %.0f GHz', rep_rate_intra_burst*1e-9), ...
                 sprintf('N pulses: %d', N_pulses_fs), ...
                 sprintf('Burst Duration: %.1f ns', burst_duration*1e9), ...
                 sprintf(''), ...
                 sprintf('\\bfPeak Pressures:\\rm'), ...
                 sprintf('NS p2p: %.2e Pa', p2p_ns), ...
                 sprintf('FS p2p: %.2e Pa', p2p_fs), ...
                 sprintf('Enhancement: %.1fx', enhancement_factor)};
text(0.98, 0.95, overlay_stats, 'Units', 'normalized', 'VerticalAlignment', 'top', ...
    'HorizontalAlignment', 'right', 'EdgeColor', 'k', 'BackgroundColor', [1 1 1 0.8], 'FontSize', 9);

% Plot 2: NS Waveform (bottom left)
subplot(2,2,3);
plot(time_vec*1e6, signal_ns, 'b-', 'LineWidth', 2);
xlabel('Time [us]');
ylabel('Pressure [Pa]');
title('NS Pulse: Waveform', 'FontWeight', 'bold');
grid on;
xlim([gate_start_time*1e6, max(kgrid.t_array)*1e6]);

ns_stats = {sprintf('\\bfNS Parameters:\\rm'), ...
            sprintf('Fluence: %.2e J/cm^2', fluence_ns_at_focus), ...
            sprintf('Pulse Energy: %.2f nJ', energy_ns_per_pulse*1e9), ...
            sprintf('Peak Intensity: %.1e W/m^2', I_focus_peak_ns), ...
            sprintf('Peak Power: %.2e W', peak_power_ns), ...
            sprintf('Pulse Width: %.1f ns', tau_ns*1e9)};
text(0.98, 0.95, ns_stats, 'Units', 'normalized', 'VerticalAlignment', 'top', ...
    'HorizontalAlignment', 'right', 'EdgeColor', 'k', 'BackgroundColor', [1 1 1 0.8], 'FontSize', 9);

% Plot 3: FS Waveform (bottom right)
subplot(2,2,4);
plot(time_vec*1e6, signal_fs, 'r-', 'LineWidth', 2);
xlabel('Time [us]');
ylabel('Pressure [Pa]');
title('FS Burst: Waveform', 'FontWeight', 'bold');
grid on;
xlim([gate_start_time*1e6, max(kgrid.t_array)*1e6]);

fs_stats = {sprintf('\\bfFS Parameters (per pulse):\\rm'), ...
            sprintf('Fluence: %.2e J/cm^2', fluence_fs_per_pulse_at_focus), ...
            sprintf('Pulse Energy: %.2f nJ', energy_fs_per_pulse*1e9), ...
            sprintf('Peak Intensity: %.1e W/m^2', I_focus_peak_fs), ...
            sprintf('Peak Power: %.2e W', peak_power_fs), ...
            sprintf('Pulse Width: %.0f fs', tau_fs*1e15)};
text(0.98, 0.95, fs_stats, 'Units', 'normalized', 'VerticalAlignment', 'top', ...
    'HorizontalAlignment', 'right', 'EdgeColor', 'k', 'BackgroundColor', [1 1 1 0.8], 'FontSize', 9);

sgtitle(sprintf('Waveforms | Target: %.0f um | Agent: %s', ...
    target_depth*1e6, contrast_agent), 'FontSize', 13, 'FontWeight', 'bold');

% -------------------------------------------------------------------------
% FIGURE 2: B-scans (2 subplots)
% -------------------------------------------------------------------------
figure('Position', [50, 800, 1000, 400]);

% Colormap
cmap_bwr = [linspace(0,1,128)', linspace(0,1,128)', ones(128,1); ...
            ones(128,1), linspace(1,0,128)', linspace(1,0,128)'];

% Plot 1: NS B-scan
subplot(1,2,1);
imagesc(kgrid.t_array*1e6, y_vec*1e6, sensor_data_ns_gated');
xlabel('Time [us]');
ylabel('Lateral y [um]');
title('NS Pulse: B-scan', 'FontWeight', 'bold');
colorbar;
colormap(gca, cmap_bwr);
max_pressure_ns = max(abs(sensor_data_ns_gated(:)));
caxis([-1 1]*max_pressure_ns);
xlim([gate_start_time*1e6, max(kgrid.t_array)*1e6]);

% Plot 2: FS B-scan
subplot(1,2,2);
imagesc(kgrid.t_array*1e6, y_vec*1e6, sensor_data_fs_gated');
xlabel('Time [us]');
ylabel('Lateral y [um]');
title('FS Burst: B-scan', 'FontWeight', 'bold');
colorbar;
colormap(gca, cmap_bwr);
max_pressure_fs = max(abs(sensor_data_fs_gated(:)));
caxis([-1 1]*max_pressure_fs);
xlim([gate_start_time*1e6, max(kgrid.t_array)*1e6]);

sgtitle(sprintf('B-scans | Target: %.0f um | Agent: %s', ...
    target_depth*1e6, contrast_agent), 'FontSize', 13, 'FontWeight', 'bold');

% -------------------------------------------------------------------------
% FIGURE 3: FFT Comparison (two separate subplots, linear scale)
% -------------------------------------------------------------------------
figure('Position', [1100, 50, 900, 400]);

Fs = 1 / kgrid.dt;  % Sampling frequency
N_fft = length(signal_ns);
f_vec = (0:N_fft-1) * Fs / N_fft;  % Frequency vector

% Compute FFT (single-sided)
fft_ns = abs(fft(signal_ns)) / N_fft;
fft_fs = abs(fft(signal_fs)) / N_fft;
fft_ns_ss = 2 * fft_ns(1:floor(N_fft/2)+1);
fft_fs_ss = 2 * fft_fs(1:floor(N_fft/2)+1);
f_vec_ss = f_vec(1:floor(N_fft/2)+1);

% Plot 1: NS FFT
subplot(1,2,1);
plot(f_vec_ss*1e-6, fft_ns_ss, 'b-', 'LineWidth', 1.5);
xlabel('Frequency [MHz]');
ylabel('Amplitude [Pa]');
title('NS Pulse: Frequency Spectrum', 'FontWeight', 'bold');
grid on;
xlim([0, min(100, max(f_vec_ss)*1e-6)]);

% Plot 2: FS FFT
subplot(1,2,2);
plot(f_vec_ss*1e-6, fft_fs_ss, 'r-', 'LineWidth', 1.5);
xlabel('Frequency [MHz]');
ylabel('Amplitude [Pa]');
title('FS Burst: Frequency Spectrum', 'FontWeight', 'bold');
grid on;
xlim([0, min(100, max(f_vec_ss)*1e-6)]);

sgtitle(sprintf('Frequency Spectra | Target: %.0f um | Agent: %s', ...
    target_depth*1e6, contrast_agent), 'FontSize', 13, 'FontWeight', 'bold');

fprintf('=================================================================\n');
fprintf('SIMULATION COMPLETE\n');
fprintf('=================================================================\n');