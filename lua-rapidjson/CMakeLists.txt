CMAKE_MINIMUM_REQUIRED(VERSION 3.7)

SET(VERSION_EXTERNAL "0.7.1")
SET(VERSION_PACKAGE "1")

PROJECT("lua-rapidjson")

SET(PROJECT_VERSION "${VERSION_EXTERNAL}.${VERSION_PACKAGE}")

INCLUDE(ExternalProject)

# Filter the jonchki configuration.
CONFIGURE_FILE(installer/lua${BUILDCFG_LUA_VERSION}/lua-rapidjson.xml
               ${CMAKE_BINARY_DIR}/lua${BUILDCFG_LUA_VERSION}-lua-rapidjson-${PROJECT_VERSION}.xml
               @ONLY)

#----------------------------------------------------------------------------
#
# Build the project.
#
IF((${BUILDCFG_ONLY_JONCHKI_CFG} STREQUAL "OFF"))
	# Select the LUA version.
	INCLUDE(${CMAKE_HOME_DIRECTORY}/cmake/muhkuh_lua.cmake)

	SET(PRJ_CMAKE_ARGS "")
	LIST(APPEND PRJ_CMAKE_ARGS "-DCMAKE_BUILD_TYPE=Release")
	LIST(APPEND PRJ_CMAKE_ARGS "-DLUA_LIBRARY=${LUA_LIBRARIES}")
	LIST(APPEND PRJ_CMAKE_ARGS "-DLUA_INCLUDE_DIR=${LUA_INCLUDE_DIR}")
	LIST(APPEND PRJ_CMAKE_ARGS "-DINSTALL_DIR_LUA_MODULES=${CMAKE_CURRENT_BINARY_DIR}/install/${INSTALL_DIR_LUA_MODULES}")
	LIST(APPEND PRJ_CMAKE_ARGS "-DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}")
	LIST(APPEND PRJ_CMAKE_ARGS "-DCMAKE_INSTALL_PREFIX=''")

	IF(${JONCHKI_PLATFORM_DIST_ID} STREQUAL "windows")
		SET(LUA_RAPIDJSON_MODULE "${CMAKE_CURRENT_BINARY_DIR}/lua-rapidjson/src/TARGET_lua_rapidjson-build/rapidjson.dll")
	ELSE(${JONCHKI_PLATFORM_DIST_ID} STREQUAL "windows")
		SET(LUA_RAPIDJSON_MODULE "${CMAKE_CURRENT_BINARY_DIR}/lua-rapidjson/src/TARGET_lua_rapidjson-build/rapidjson.so")
	ENDIF(${JONCHKI_PLATFORM_DIST_ID} STREQUAL "windows")

	ExternalProject_Add(TARGET_lua_rapidjson
	                    PREFIX ${CMAKE_CURRENT_BINARY_DIR}/lua-rapidjson
	                    URL ${CMAKE_CURRENT_SOURCE_DIR}/lua-rapidjson-${VERSION_EXTERNAL}.tar.gz
	                    URL_HASH SHA1=09322ef9a91596afbc2bf5303a8aa7c1c10af78d
	                    PATCH_COMMAND "${PYTHON_INTERPRETER}" ${CMAKE_HOME_DIRECTORY}/cmake/tools/apply_patches.py --working-folder ${CMAKE_CURRENT_BINARY_DIR}/lua-rapidjson/src/TARGET_lua_rapidjson --patch-folder ${CMAKE_CURRENT_SOURCE_DIR}/patches --strip 1
	                    CMAKE_ARGS ${PRJ_CMAKE_ARGS}
	                    INSTALL_COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_BINARY_DIR}/install/lua_plugins/ && ${CMAKE_COMMAND} -E copy ${LUA_RAPIDJSON_MODULE} ${CMAKE_CURRENT_BINARY_DIR}/install/lua_plugins/
	)

	IF((CMAKE_SYSTEM_NAME STREQUAL "Windows") AND (${CMAKE_COMPILER_IS_GNUCC}))
		# Here are the MinGW specific tests.
		ADD_TEST(NAME lua_rapidjson_MinGW_DLL_dependencies
		         COMMAND "${PYTHON_INTERPRETER}" ${CMAKE_SOURCE_DIR}/cmake/tests/mingw_dll_dependencies.py -u lua5.1 -u lua5.2 -u lua5.3 -u lua5.4 ${LUA_RAPIDJSON_MODULE})
	ENDIF((CMAKE_SYSTEM_NAME STREQUAL "Windows") AND (${CMAKE_COMPILER_IS_GNUCC}))


	#----------------------------------------------------------------------------
	#
	# Build a package for the selected platform.
	#
	SET(CPACK_OUTPUT_FILE_PREFIX ${CMAKE_BINARY_DIR}/../../repository/com/github/xpol/lua-rapidjson/${PROJECT_VERSION})
	SET(CPACK_INCLUDE_TOPLEVEL_DIRECTORY FALSE)
	SET(CPACK_PACKAGE_FILE_NAME "lua${BUILDCFG_LUA_VERSION}-lua-rapidjson-${PROJECT_VERSION}-${JONCHKI_PLATFORM}")

	SET(CPACK_GENERATOR "TXZ")
	INCLUDE(CPack)

	IF(${JONCHKI_PLATFORM_DIST_ID} STREQUAL "windows")
		# Package a windows build.

		CONFIGURE_FILE(installer/install_windows.lua
		               ${CMAKE_CURRENT_BINARY_DIR}/package/install.lua
		               @ONLY)
	ELSE(${JONCHKI_PLATFORM_DIST_ID} STREQUAL "windows")
		# Package a linux build.

		CONFIGURE_FILE(installer/install_linux.lua
		               ${CMAKE_CURRENT_BINARY_DIR}/package/install.lua
		               @ONLY)
	ENDIF(${JONCHKI_PLATFORM_DIST_ID} STREQUAL "windows")

	INSTALL(FILES ${LUA_RAPIDJSON_MODULE}
	        DESTINATION ${INSTALL_DIR_LUA_MODULES})

#	INSTALL(FILES ${CMAKE_CURRENT_BINARY_DIR}/lua-rapidjson/src/TARGET_lua_rapidjson/lua/rapidjson/util.lua
#	        DESTINATION ${INSTALL_DIR_LUA_SCRIPTS}/rapidjson)

	INSTALL(FILES ${CMAKE_CURRENT_BINARY_DIR}/package/install.lua
	        DESTINATION .)

	CONFIGURE_FILE(installer/lua${BUILDCFG_LUA_VERSION}/lua-rapidjson.xml
	               ${CPACK_OUTPUT_FILE_PREFIX}/lua${BUILDCFG_LUA_VERSION}-lua-rapidjson-${PROJECT_VERSION}-${JONCHKI_PLATFORM}.xml
	               @ONLY)


	#-----------------------------------------------------------------------------
	#
	# Create a custom target named "pack".
	# It builds the package and creates the hashes.
	#
	ADD_CUSTOM_TARGET(pack
	                  COMMAND ${CMAKE_MAKE_PROGRAM}
	                  COMMAND ${CMAKE_MAKE_PROGRAM} package
	                  COMMAND "${PYTHON_INTERPRETER}" ${CMAKE_HOME_DIRECTORY}/cmake/tools/generate_hash.py ${CPACK_OUTPUT_FILE_PREFIX}/lua${BUILDCFG_LUA_VERSION}-lua-rapidjson-${PROJECT_VERSION}-${JONCHKI_PLATFORM}.xml
	                  COMMAND "${PYTHON_INTERPRETER}" ${CMAKE_HOME_DIRECTORY}/cmake/tools/generate_hash.py ${CPACK_OUTPUT_FILE_PREFIX}/lua${BUILDCFG_LUA_VERSION}-lua-rapidjson-${PROJECT_VERSION}-${JONCHKI_PLATFORM}.tar.xz
	                  COMMENT "Pack the artifact and generate the hashes...")


	#-----------------------------------------------------------------------------
	#
	# Filter the pom.xml file.
	#
	SET(POM_ARTIFACT_ID  "lua${BUILDCFG_LUA_VERSION}-lua-rapidjson")
	SET(POM_GROUP_ID     "com.github.xpol")
	SET(POM_VERSION      "${PROJECT_VERSION}")
	SET(POM_PACKAGING    "tar.xz")
	CONFIGURE_FILE(installer/pom.xml
	               ${CPACK_OUTPUT_FILE_PREFIX}/lua${BUILDCFG_LUA_VERSION}-lua-rapidjson-${PROJECT_VERSION}.pom
	               @ONLY)
ENDIF((${BUILDCFG_ONLY_JONCHKI_CFG} STREQUAL "OFF"))
