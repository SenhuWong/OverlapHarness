cmake_minimum_required(VERSION 3.20)

project(OverlapHarnessSuperbuild LANGUAGES NONE)

include(ExternalProject)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type for dependencies and solver variants" FORCE)
endif()

set(OVERLAP_ARTIFACTS_DIR
    "${CMAKE_SOURCE_DIR}/artifacts"
    CACHE PATH "Root for generated build and install artifacts")
set(OVERLAP_BUILD_ROOT "${OVERLAP_ARTIFACTS_DIR}/build")
set(OVERLAP_INSTALL_ROOT "${OVERLAP_ARTIFACTS_DIR}/install")

set(OVERLAP_HDF5_SOURCE_DIR "${CMAKE_SOURCE_DIR}/solver/vendor/HDF5")
set(OVERLAP_HDF5_BUILD_DIR "${OVERLAP_BUILD_ROOT}/dependencies/hdf5")
set(OVERLAP_HDF5_INSTALL_DIR "${OVERLAP_INSTALL_ROOT}/hdf5")

if(NOT EXISTS "${OVERLAP_HDF5_SOURCE_DIR}/CMakeLists.txt")
    message(FATAL_ERROR
        "HDF5 submodule is missing. Run: git submodule update --init --recursive")
endif()

ExternalProject_Add(hdf5-parallel
    SOURCE_DIR "${OVERLAP_HDF5_SOURCE_DIR}"
    BINARY_DIR "${OVERLAP_HDF5_BUILD_DIR}"
    INSTALL_DIR "${OVERLAP_HDF5_INSTALL_DIR}"
    PREFIX "${CMAKE_BINARY_DIR}/external/hdf5-parallel"
    DOWNLOAD_COMMAND ""
    UPDATE_COMMAND ""
    CMAKE_ARGS
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>
        -DBUILD_SHARED_LIBS=ON
        -DBUILD_STATIC_LIBS=ON
        -DBUILD_TESTING=OFF
        -DHDF5_BUILD_CPP_LIB=OFF
        -DHDF5_BUILD_EXAMPLES=OFF
        -DHDF5_BUILD_FORTRAN=OFF
        -DHDF5_BUILD_HL_LIB=OFF
        -DHDF5_BUILD_JAVA=OFF
        -DHDF5_BUILD_TOOLS=OFF
        -DHDF5_ENABLE_PARALLEL=ON
    BUILD_ALWAYS ON
    EXCLUDE_FROM_ALL TRUE
    USES_TERMINAL_CONFIGURE TRUE
    USES_TERMINAL_BUILD TRUE
    USES_TERMINAL_INSTALL TRUE
)

set(_overlap_solver_targets)

function(overlap_add_solver_variant dimension model)
    string(TOLOWER "${model}" model_lower)
    set(variant "${dimension}d-${model_lower}")
    set(target "solver-${variant}")
    set(binary_dir "${OVERLAP_BUILD_ROOT}/solver/${variant}")

    ExternalProject_Add("${target}"
        SOURCE_DIR "${CMAKE_SOURCE_DIR}/solver"
        BINARY_DIR "${binary_dir}"
        PREFIX "${CMAKE_BINARY_DIR}/external/${target}"
        DOWNLOAD_COMMAND ""
        UPDATE_COMMAND ""
        CMAKE_ARGS
            -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
            -DAMReX_SPACEDIM=${dimension}
            -DTURB_MODEL=${model}
            -DHDF5_DIR=${OVERLAP_HDF5_INSTALL_DIR}/cmake
        BUILD_ALWAYS ON
        INSTALL_COMMAND ""
        DEPENDS hdf5-parallel
        EXCLUDE_FROM_ALL TRUE
        USES_TERMINAL_CONFIGURE TRUE
        USES_TERMINAL_BUILD TRUE
    )

    list(APPEND _overlap_solver_targets "${target}")
    set(_overlap_solver_targets "${_overlap_solver_targets}" PARENT_SCOPE)
endfunction()

foreach(dimension IN ITEMS 2 3)
    foreach(model IN ITEMS EULER SST SA)
        overlap_add_solver_variant("${dimension}" "${model}")
    endforeach()
endforeach()

add_custom_target(solver-matrix DEPENDS ${_overlap_solver_targets})
