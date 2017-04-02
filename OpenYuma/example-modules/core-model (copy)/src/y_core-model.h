
#ifndef _H_y_core_model
#define _H_y_core_model
/* 
 * Copyright (c) 2008-2012, Andy Bierman, All Rights Reserved.
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 *

*** Generated by yangdump 2.5-5

    Yuma SIL header
    module core-model
    revision 2017-02-17
    namespace urn:onf:params:xml:ns:yang:CoreModel
    organization ONF (Open Networking Foundation) Open Transport Working Group - Wireless Transport Project

 */

#include <xmlstring.h>

#include "dlq.h"
#include "ncxtypes.h"
#include "op.h"
#include "status.h"
#include "val.h"

#ifdef __cplusplus
extern "C" {
#endif

#define y_core_model_M_core_model (const xmlChar *)"core-model"
#define y_core_model_R_core_model (const xmlChar *)"2017-02-17"

#define y_core_model_N_action_verb (const xmlChar *)"action-verb"
#define y_core_model_N_actual_equipment (const xmlChar *)"actual-equipment"
#define y_core_model_N_actual_holder (const xmlChar *)"actual-holder"
#define y_core_model_N_address_element (const xmlChar *)"address-element"
#define y_core_model_N_address_element_name (const xmlChar *)"address-element-name"
#define y_core_model_N_address_name (const xmlChar *)"address-name"
#define y_core_model_N_administrative_control (const xmlChar *)"administrative-control"
#define y_core_model_N_administrative_state (const xmlChar *)"administrative-state"
#define y_core_model_N_after_operation_set (const xmlChar *)"after-operation-set"
#define y_core_model_N_aggregate_function (const xmlChar *)"aggregate-function"
#define y_core_model_N_arbitrary_element (const xmlChar *)"arbitrary-element"
#define y_core_model_N_asset_instance_identifier (const xmlChar *)"asset-instance-identifier"
#define y_core_model_N_asset_type_identifier (const xmlChar *)"asset-type-identifier"
#define y_core_model_N_before_operation_set (const xmlChar *)"before-operation-set"
#define y_core_model_N_category (const xmlChar *)"category"
#define y_core_model_N_class_of_instance (const xmlChar *)"class-of-instance"
#define y_core_model_N_client_ltp (const xmlChar *)"client-ltp"
#define y_core_model_N_config_and_switch_controller (const xmlChar *)"config-and-switch-controller"
#define y_core_model_N_configured_client_capacity (const xmlChar *)"configured-client-capacity"
#define y_core_model_N_connected_ltp (const xmlChar *)"connected-ltp"
#define y_core_model_N_connector (const xmlChar *)"connector"
#define y_core_model_N_connector_type (const xmlChar *)"connector-type"
#define y_core_model_N_contained_holder (const xmlChar *)"contained-holder"
#define y_core_model_N_control_parameters (const xmlChar *)"control-parameters"
#define y_core_model_N_description (const xmlChar *)"description"
#define y_core_model_N_effort_and_action (const xmlChar *)"effort-and-action"
#define y_core_model_N_equipment (const xmlChar *)"equipment"
#define y_core_model_N_equipment_instance (const xmlChar *)"equipment-instance"
#define y_core_model_N_equipment_location (const xmlChar *)"equipment-location"
#define y_core_model_N_equipment_type (const xmlChar *)"equipment-type"
#define y_core_model_N_expected_equipment (const xmlChar *)"expected-equipment"
#define y_core_model_N_expected_holder (const xmlChar *)"expected-holder"
#define y_core_model_N_exposed_cable (const xmlChar *)"exposed-cable"
#define y_core_model_N_extension (const xmlChar *)"extension"
#define y_core_model_N_fc (const xmlChar *)"fc"
#define y_core_model_N_fc_blocks_signal_to_lp (const xmlChar *)"fc-blocks-signal-to-lp"
#define y_core_model_N_fc_port (const xmlChar *)"fc-port"
#define y_core_model_N_fc_port_direction (const xmlChar *)"fc-port-direction"
#define y_core_model_N_fc_route (const xmlChar *)"fc-route"
#define y_core_model_N_fc_route_feeds_fc_port_egress (const xmlChar *)"fc-route-feeds-fc-port-egress"
#define y_core_model_N_fc_switch (const xmlChar *)"fc-switch"
#define y_core_model_N_fd (const xmlChar *)"fd"
#define y_core_model_N_fire_characteristics (const xmlChar *)"fire-characteristics"
#define y_core_model_N_forwarding_construct (const xmlChar *)"forwarding-construct"
#define y_core_model_N_forwarding_direction (const xmlChar *)"forwarding-direction"
#define y_core_model_N_function_block (const xmlChar *)"function-block"
#define y_core_model_N_function_enablers (const xmlChar *)"function-enablers"
#define y_core_model_N_generaldirectives (const xmlChar *)"generaldirectives"
#define y_core_model_N_geographical_location (const xmlChar *)"geographical-location"
#define y_core_model_N_global_pac (const xmlChar *)"global-pac"
#define y_core_model_N_height (const xmlChar *)"height"
#define y_core_model_N_hold_off_time (const xmlChar *)"hold-off-time"
#define y_core_model_N_holder_category (const xmlChar *)"holder-category"
#define y_core_model_N_holder_location (const xmlChar *)"holder-location"
#define y_core_model_N_holder_monitors (const xmlChar *)"holder-monitors"
#define y_core_model_N_holder_structure (const xmlChar *)"holder-structure"
#define y_core_model_N_internal_configuration_and_switch_control (const xmlChar *)"internal-configuration-and-switch-control"
#define y_core_model_N_is_active (const xmlChar *)"is-active"
#define y_core_model_N_is_actual_mismatch_with_expected (const xmlChar *)"is-actual-mismatch-with-expected"
#define y_core_model_N_is_captive (const xmlChar *)"is-captive"
#define y_core_model_N_is_coordinated_switching_both_ends (const xmlChar *)"is-coordinated-switching-both-ends"
#define y_core_model_N_is_field_replaceable (const xmlChar *)"is-field-replaceable"
#define y_core_model_N_is_frozen (const xmlChar *)"is-frozen"
#define y_core_model_N_is_guided (const xmlChar *)"is-guided"
#define y_core_model_N_is_hot_swappable (const xmlChar *)"is-hot-swappable"
#define y_core_model_N_is_internal_port (const xmlChar *)"is-internal-port"
#define y_core_model_N_is_not (const xmlChar *)"is-not"
#define y_core_model_N_is_protection_lock_out (const xmlChar *)"is-protection-lock-out"
#define y_core_model_N_is_quantized_space (const xmlChar *)"is-quantized-space"
#define y_core_model_N_is_short_lived (const xmlChar *)"is-short-lived"
#define y_core_model_N_label (const xmlChar *)"label"
#define y_core_model_N_layer_protocol_name (const xmlChar *)"layer-protocol-name"
#define y_core_model_N_length (const xmlChar *)"length"
#define y_core_model_N_lifecycle_state (const xmlChar *)"lifecycle-state"
#define y_core_model_N_local_id (const xmlChar *)"local-id"
#define y_core_model_N_local_pac (const xmlChar *)"local-pac"
#define y_core_model_N_location (const xmlChar *)"location"
#define y_core_model_N_lower_level_fc (const xmlChar *)"lower-level-fc"
#define y_core_model_N_lower_level_fd (const xmlChar *)"lower-level-fd"
#define y_core_model_N_lower_level_link (const xmlChar *)"lower-level-link"
#define y_core_model_N_lp (const xmlChar *)"lp"
#define y_core_model_N_lp_direction (const xmlChar *)"lp-direction"
#define y_core_model_N_ltp (const xmlChar *)"ltp"
#define y_core_model_N_ltp_direction (const xmlChar *)"ltp-direction"
#define y_core_model_N_ltp_in_other_view (const xmlChar *)"ltp-in-other-view"
#define y_core_model_N_manufacture_date (const xmlChar *)"manufacture-date"
#define y_core_model_N_manufactured_thing (const xmlChar *)"manufactured-thing"
#define y_core_model_N_manufacturer_identifier (const xmlChar *)"manufacturer-identifier"
#define y_core_model_N_manufacturer_name (const xmlChar *)"manufacturer-name"
#define y_core_model_N_manufacturer_properties (const xmlChar *)"manufacturer-properties"
#define y_core_model_N_materials (const xmlChar *)"materials"
#define y_core_model_N_mechanical_features (const xmlChar *)"mechanical-features"
#define y_core_model_N_mechanical_functions (const xmlChar *)"mechanical-functions"
#define y_core_model_N_model_identifier (const xmlChar *)"model-identifier"
#define y_core_model_N_name (const xmlChar *)"name"
#define y_core_model_N_necessary_initialcondition_constraints (const xmlChar *)"necessary-initialcondition-constraints"
#define y_core_model_N_network_element (const xmlChar *)"network-element"
#define y_core_model_N_network_scheme_specification (const xmlChar *)"network-scheme-specification"
#define y_core_model_N_occupying_fru (const xmlChar *)"occupying-fru"
#define y_core_model_N_operation_details (const xmlChar *)"operation-details"
#define y_core_model_N_operation_envelope (const xmlChar *)"operation-envelope"
#define y_core_model_N_operation_set (const xmlChar *)"operation-set"
#define y_core_model_N_operational_state (const xmlChar *)"operational-state"
#define y_core_model_N_operationidentifiers (const xmlChar *)"operationidentifiers"
#define y_core_model_N_operationset (const xmlChar *)"operationset"
#define y_core_model_N_operator_augmented_equipment_type (const xmlChar *)"operator-augmented-equipment-type"
#define y_core_model_N_orientation (const xmlChar *)"orientation"
#define y_core_model_N_part_type_identifier (const xmlChar *)"part-type-identifier"
#define y_core_model_N_pause_resume_rule (const xmlChar *)"pause-resume-rule"
#define y_core_model_N_peer_ltp (const xmlChar *)"peer-ltp"
#define y_core_model_N_physical_characteristics (const xmlChar *)"physical-characteristics"
#define y_core_model_N_physical_port_reference (const xmlChar *)"physical-port-reference"
#define y_core_model_N_physical_properties (const xmlChar *)"physical-properties"
#define y_core_model_N_physical_rating (const xmlChar *)"physical-rating"
#define y_core_model_N_pin (const xmlChar *)"pin"
#define y_core_model_N_pin_layout (const xmlChar *)"pin-layout"
#define y_core_model_N_position (const xmlChar *)"position"
#define y_core_model_N_power_rating (const xmlChar *)"power-rating"
#define y_core_model_N_power_state (const xmlChar *)"power-state"
#define y_core_model_N_profile_proxy (const xmlChar *)"profile-proxy"
#define y_core_model_N_prot_type (const xmlChar *)"prot-type"
#define y_core_model_N_relative_position (const xmlChar *)"relative-position"
#define y_core_model_N_reversion_mode (const xmlChar *)"reversion-mode"
#define y_core_model_N_role (const xmlChar *)"role"
#define y_core_model_N_rotation_speed (const xmlChar *)"rotation-speed"
#define y_core_model_N_selected_fc_port (const xmlChar *)"selected-fc-port"
#define y_core_model_N_selection_priority (const xmlChar *)"selection-priority"
#define y_core_model_N_serial_number (const xmlChar *)"serial-number"
#define y_core_model_N_server_ltp (const xmlChar *)"server-ltp"
#define y_core_model_N_service_priority (const xmlChar *)"service-priority"
#define y_core_model_N_spatial_properties_of_type (const xmlChar *)"spatial-properties-of-type"
#define y_core_model_N_subordinate_controller (const xmlChar *)"subordinate-controller"
#define y_core_model_N_supported_equipment (const xmlChar *)"supported-equipment"
#define y_core_model_N_supported_link (const xmlChar *)"supported-link"
#define y_core_model_N_swapability (const xmlChar *)"swapability"
#define y_core_model_N_switch_control (const xmlChar *)"switch-control"
#define y_core_model_N_switch_rule (const xmlChar *)"switch-rule"
#define y_core_model_N_switch_selection_reason (const xmlChar *)"switch-selection-reason"
#define y_core_model_N_switch_selects_ports (const xmlChar *)"switch-selects-ports"
#define y_core_model_N_temperature (const xmlChar *)"temperature"
#define y_core_model_N_termination_state (const xmlChar *)"termination-state"
#define y_core_model_N_thermal_rating (const xmlChar *)"thermal-rating"
#define y_core_model_N_type_name (const xmlChar *)"type-name"
#define y_core_model_N_uuid (const xmlChar *)"uuid"
#define y_core_model_N_value (const xmlChar *)"value"
#define y_core_model_N_value_name (const xmlChar *)"value-name"
#define y_core_model_N_version (const xmlChar *)"version"
#define y_core_model_N_wait_to_restore_time (const xmlChar *)"wait-to-restore-time"
#define y_core_model_N_wait_to_revert_time (const xmlChar *)"wait-to-revert-time"
#define y_core_model_N_weight_characteristics (const xmlChar *)"weight-characteristics"
#define y_core_model_N_width (const xmlChar *)"width"
/********************************************************************
* FUNCTION y_core_model_init
* 
* initialize the core-model server instrumentation library
* 
* INPUTS:
*    modname == requested module name
*    revision == requested version (NULL for any)
* 
* RETURNS:
*     error status
********************************************************************/
extern status_t y_core_model_init (
    const xmlChar *modname,
    const xmlChar *revision);

/********************************************************************
* FUNCTION y_core_model_init2
* 
* SIL init phase 2: non-config data structures
* Called after running config is loaded
* 
* RETURNS:
*     error status
********************************************************************/
extern status_t y_core_model_init2 (void);

/********************************************************************
* FUNCTION y_core_model_cleanup
*    cleanup the server instrumentation library
* 
********************************************************************/
extern void y_core_model_cleanup (void);

#ifdef __cplusplus
} /* end extern 'C' */
#endif

#endif