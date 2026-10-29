Name:		python-torchvulkan
Version:	0.2.1
Release:	1
Summary:	Vulkan compute backend for PyTorch
License:	MIT
Group:		Development/Python
URL:		https://github.com/ZainSharief/torchvulkan
Source0:	https://github.com/ZainSharief/torchvulkan/archive/refs/tags/v%{version}.tar.gz#/torchvulkan-%{version}.tar.gz
# Drop the torch==2.13.0 build pin, link the system torch without
# LoadHIP, and compile shaders with slangc -O2.
Patch0:		torchvulkan-no-torch-pin.patch

BuildRequires:	python
BuildRequires:	pkgconfig(python3)
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	python%{pyver}dist(scikit-build-core)
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:	python%{pyver}dist(setuptools-scm)
BuildRequires:	python%{pyver}dist(wheel)
# Private headers (torch/csrc/Generator.h). Rebuild when the torch
# C++ ABI changes. 2.15 is the first cooker torch this is built for.
BuildRequires:	python%{pyver}dist(torch) >= 2.15
# slangc -O2 compiles the Slang kernels to SPIR-V. Needs
# shader-slang 2026.18.3-2, which fixes the optimizer options ABI.
BuildRequires:	shader-slang >= 2026.18.3-2
BuildRequires:	pkgconfig(vulkan)

# volk dlopens libvulkan.so.1. The ELF generator does not see that.
Requires:	vulkan-loader
Requires:	python%{pyver}dist(torch) >= 2.15

%description
torchvulkan registers a Vulkan device with PyTorch and runs tensor
ops as Vulkan compute shaders. Importing it claims the "vulkan"
device name (PrivateUse1). That name then takes priority over the
in-tree ATen Vulkan backend built into python-torch.

Most operators run on the GPU. The ones that do not fall back to
the CPU, including during training. TORCHVULKAN_STRICT=1 turns
those fallbacks into errors.

Shaders are written in Slang, compiled to SPIR-V when this package
is built, and embedded in the extension. A Vulkan 1.3 driver is
needed at runtime. volk is bundled and loads the system Vulkan
loader; VulkanMemoryAllocator is the bundled header.

%prep
%autosetup -n torchvulkan-%{version} -p1

%build
# The GitHub tag archive has no .git. setuptools_scm needs a version.
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_TORCHVULKAN=%{version}
# Patch0 reads Torch_DIR. The ROCm Torch config would enable HIP.
export Torch_DIR=%{python_sitearch}/torch/share/cmake/Torch
export CMAKE_PREFIX_PATH="%{python_sitearch}/torch${CMAKE_PREFIX_PATH:+:$CMAKE_PREFIX_PATH}"
export CMAKE_ARGS="-DTorch_DIR=%{python_sitearch}/torch/share/cmake/Torch -DCMAKE_PREFIX_PATH=%{python_sitearch}/torch"
mkdir -p ../wheels
pip wheel --wheel-dir ../wheels --no-deps --no-build-isolation --verbose .

%install
pip install --root=%{buildroot} --no-deps --verbose --ignore-installed \
	--no-warn-script-location --no-index --no-cache-dir \
	--find-links ../wheels ../wheels/*.whl

%files
%license LICENSE licenses/MoltenVK-LICENSE
%doc README.md
%{python_sitearch}/torchvulkan
%{python_sitearch}/torchvulkan-*.*-info
