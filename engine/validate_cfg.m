function validate_cfg(cfg)
% VALIDATE_CFG  Check cfg struct before running run_pa_sim.
%
%   validate_cfg(cfg)
%
%   Throws an error with a clear message if any field is missing or
%   physically invalid.  Call this at the top of run_pa_sim.

% -------------------------------------------------------------------------
% Required fields
% -------------------------------------------------------------------------
required = { ...
    'lambda', 'NA', 'n', 'target_depth', 'target_radius', ...
    'fluence_focus', 'pulse_duration', 'Gamma', ...
    'mu_a_tissue', 'mu_s_tissue', ...
    'mu_a_target', 'mu_s_target', 'alpha2_target', 'alpha3_target', ...
    'c_sound', 'rho', 'alpha_coeff', 'alpha_power', ...
    'f_transducer', 'PPW_acoustic', 'n_elements', ...
    'z_max', 'y_max', 'PPW_optical', 'opt_margin'};

for k = 1:numel(required)
    if ~isfield(cfg, required{k})
        error('validate_cfg: missing required field ''%s''.', required{k});
    end
end

% -------------------------------------------------------------------------
% Positive-definite scalars (must be > 0)
% -------------------------------------------------------------------------
positive = {'lambda','NA','n','target_depth','target_radius', ...
            'fluence_focus','pulse_duration','Gamma', ...
            'mu_a_tissue','mu_s_tissue', ...
            'c_sound','rho','f_transducer','PPW_acoustic','n_elements', ...
            'z_max','y_max','PPW_optical','opt_margin'};

for k = 1:numel(positive)
    v = cfg.(positive{k});
    if ~isscalar(v) || ~isnumeric(v) || v <= 0
        error('validate_cfg: ''%s'' must be a positive scalar (got %s).', ...
              positive{k}, mat2str(v));
    end
end

% -------------------------------------------------------------------------
% Non-negative scalars (may be zero — e.g. contrast agent with no linear absorption)
% -------------------------------------------------------------------------
nonneg = {'mu_a_target', 'mu_s_target', 'alpha2_target', 'alpha3_target'};

for k = 1:numel(nonneg)
    v = cfg.(nonneg{k});
    if ~isscalar(v) || ~isnumeric(v) || v < 0
        error('validate_cfg: ''%s'' must be a non-negative scalar (got %s).', ...
              nonneg{k}, mat2str(v));
    end
end

% -------------------------------------------------------------------------
% Physical constraints
% -------------------------------------------------------------------------
if cfg.NA >= cfg.n
    error('validate_cfg: NA (%.4f) must be less than refractive index n (%.4f).', ...
          cfg.NA, cfg.n);
end

if cfg.target_depth >= cfg.z_max
    error('validate_cfg: target_depth (%.2f mm) must be less than z_max (%.2f mm).', ...
          cfg.target_depth*1e3, cfg.z_max*1e3);
end

if cfg.target_depth + cfg.target_radius > cfg.z_max
    error('validate_cfg: target extends beyond z_max (target_depth + target_radius = %.2f mm, z_max = %.2f mm).', ...
          (cfg.target_depth + cfg.target_radius)*1e3, cfg.z_max*1e3);
end

if cfg.target_radius > cfg.y_max
    error('validate_cfg: target_radius (%.2f um) exceeds lateral half-extent y_max (%.2f mm).', ...
          cfg.target_radius*1e6, cfg.y_max*1e3);
end

% -------------------------------------------------------------------------
% Optional: burst_N (positive integer) and burst_tau (required if burst_N > 1)
% -------------------------------------------------------------------------
if isfield(cfg, 'burst_N')
    v = cfg.burst_N;
    if ~isscalar(v) || ~isnumeric(v) || v < 1 || floor(v) ~= v
        error('validate_cfg: ''burst_N'' must be a positive integer (got %s).', mat2str(v));
    end
    if v > 1 && ~isfield(cfg, 'burst_tau')
        error('validate_cfg: ''burst_tau'' (burst window duration) is required when burst_N > 1.');
    end
end

if isfield(cfg, 'burst_tau')
    v = cfg.burst_tau;
    if ~isscalar(v) || ~isnumeric(v) || v <= 0
        error('validate_cfg: ''burst_tau'' must be a positive scalar (got %s).', mat2str(v));
    end
end

% -------------------------------------------------------------------------
% Warnings (physically possible but likely unintended)
% -------------------------------------------------------------------------
pml_size = 20;
if isfield(cfg, 'pml_size'), pml_size = cfg.pml_size; end
if pml_size < 20
    warning('validate_cfg: pml_size = %d is small and may cause back-wall reflections. Recommended >= 20.', pml_size);
end

if cfg.PPW_acoustic < 6
    warning('validate_cfg: PPW_acoustic = %d is low. Recommended >= 6 for accuracy.', cfg.PPW_acoustic);
end

if cfg.PPW_optical < 3
    warning('validate_cfg: PPW_optical = %d is low. Recommended >= 3.', cfg.PPW_optical);
end

clearance = cfg.z_max - cfg.target_depth;
if clearance < 1e-3
    warning('validate_cfg: only %.2f mm clearance between target_depth and z_max. Consider increasing z_max.', clearance*1e3);
end
