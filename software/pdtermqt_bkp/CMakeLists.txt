cmake_minimum_required(VERSION 3.16)
project(SerialTerminal)

# Configurações específicas para Qt6
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

# Encontre os módulos necessários do Qt6
# Encontre os módulos necessários do Qt6
find_package(Qt6 REQUIRED COMPONENTS 
    Core
    Gui
    Widgets
    SerialPort
)

set(HEADERS PdTermSerial.h PdTermTerminal.h PdTermXmodem.h PdTermDisplay.h)

set(SOURCES main.cpp PdTermSerial.cpp PdTermTerminal.cpp PdTermXmodem.cpp PdTermDisplay.cpp)

# Adicione seu executável
add_executable(SerialTerminal  ${SOURCES} ${HEADERS})

# Vincule as bibliotecas necessárias
target_link_libraries(SerialTerminal
    Qt6::Core
    Qt6::Gui
    Qt6::Widgets
    Qt6::SerialPort
)

# Configuração adicional para incluir diretórios
target_include_directories(SerialTerminal PRIVATE
    ${Qt6Core_INCLUDE_DIRS}
    ${Qt6Gui_INCLUDE_DIRS}
    ${Qt6Widgets_INCLUDE_DIRS}
    ${Qt6SerialPort_INCLUDE_DIRS}
)


# Desative AUTOMOC para este arquivo específico
set_source_files_properties(main.cpp PROPERTIES SKIP_AUTOMOC ON)

# Em seguida, execute o moc manualmente
qt6_generate_moc(main.cpp main.moc)
target_sources(SerialTerminal PRIVATE main.moc)




#**************************************************


