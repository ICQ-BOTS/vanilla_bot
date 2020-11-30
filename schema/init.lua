box.cfg {
    listen = 3301
}

box.schema.user.grant('guest', 'read,write,execute', 'universe', nil, { if_not_exists = true })
box.schema.user.passwd('pass')


function init()

--------------------------------Statistics--------------------------------

if box.space.statistics == nil then
	local statistics = box.schema.space.create('statistics', { if_not_exists = true })
	
	statistics:format({
		{ name = 'user_id', 	type = 'string' },
		{ name = 'count', 		type = 'integer' }
	})


	statistics:create_index('primary', { type = 'hash', parts = { 'user_id' }, if_not_exists = true, unique = true })
	
end

--------------------------------User last history--------------------------------

if box.space.user_last_history == nil then
	local user_last_history = box.schema.space.create('user_last_history', { if_not_exists = true })
	
	user_last_history:format({
		{ name = 'user_id', 			type = 'string' },
		{ name = 'current_image_id', 	type = 'string' },
		{ name = 'last_image_id', 		type = 'string' }
	})


	user_last_history:create_index('primary', { type = 'hash', parts = { 'user_id' }, if_not_exists = true, unique = true })
	
end

end

function push_to_history(user_id, file_id)
	history_row = box.space.user_last_history:select( {user_id} )[1]
	if history_row ~= nil then
		box.space.user_last_history:update( {user_id}, { { '=', 3, history_row[2] }, { '=', 2, file_id } } )
	else
		box.space.user_last_history:insert( {user_id, file_id, '' } )
	end
end

function get_last_image(user_id)
	history_row = box.space.user_last_history:select( {user_id} )[1]
	if history_row ~= nil then
		return history_row[3]
	end
	return ''
end

function reinit()
	reinitArray = { 
		--box.space.users, 
		--box.space.tests, 
		--box.sequence.tests_ids_autoinc, 
		--box.space.questions, 
		--box.sequence.questions_ids_autoinc, 
		--box.space.tests_results,
		--box.sequence.tests_results_ids_autoinc, 
		--box.space.answers,
		--box.sequence.answers_ids_autoinc,
		box.space.statistics,
		box.space.user_last_history
	}
	for key, value in pairs(reinitArray) do
		if value ~= nil then
			value:drop()
		end
	end
	
	
	init()
end



--reinit()

box.once("data", init)